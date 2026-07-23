"""Checkpointed Qwen Q4 completion-audit client with an owned llama.cpp server."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import socket
import subprocess
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MODULUS = 1 << 128


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_bytes(value))
    for attempt in range(50):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == 49:
                raise
            time.sleep(min(0.01 * (2 ** min(attempt, 4)), 0.1))


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as handle:
        handle.write(canonical_bytes(value))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_prompts(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("prompt manifest has no rows")
    prompts: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        prompt = str(row["prompt"])
        prompts.append(
            {
                "row_id": str(row.get("row_id", f"row-{index:06d}")),
                "prompt": prompt,
                "prompt_sha256": str(
                    row.get("prompt_sha256", hashlib.sha256(prompt.encode("utf-8")).hexdigest())
                ),
            }
        )
    return prompts


def port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.25)
        return probe.connect_ex((host, port)) == 0


def http_json(url: str, payload: dict[str, Any] | None, timeout: float) -> dict[str, Any]:
    data = None if payload is None else canonical_bytes(payload)
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_server(base_url: str, process: subprocess.Popen[Any], timeout: float) -> None:
    deadline = time.monotonic() + timeout
    last_error = "server not queried"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"llama-server exited during startup with code {process.returncode}")
        try:
            http_json(f"{base_url}/health", None, timeout=2.0)
            return
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = repr(error)
            time.sleep(1.0)
    raise TimeoutError(f"llama-server health timeout: {last_error}")


def gpu_temperature_c() -> float:
    output = subprocess.check_output(
        [
            "nvidia-smi",
            "--query-gpu=temperature.gpu",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        timeout=10.0,
    )
    first_line = output.splitlines()[0].strip()
    temperature = float(first_line)
    if not math.isfinite(temperature):
        raise ValueError(f"non-finite GPU temperature: {first_line!r}")
    return temperature


def wait_for_thermal_window(
    args: argparse.Namespace,
    events_path: Path,
    progress_path: Path,
    progress: dict[str, Any],
) -> None:
    if args.thermal_pause_temperature <= 0:
        return

    temperature = gpu_temperature_c()
    progress["maximum_runner_observed_temperature_c"] = max(
        float(progress["maximum_runner_observed_temperature_c"]),
        temperature,
    )
    if temperature < args.thermal_pause_temperature:
        return

    progress["thermal_pause_count"] += 1
    pause_started = time.perf_counter()
    append_jsonl(
        events_path,
        {
            "event": "thermal_pause_start",
            "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "temperature_c": temperature,
            "pause_temperature_c": args.thermal_pause_temperature,
            "resume_temperature_c": args.thermal_resume_temperature,
        },
    )
    atomic_json(progress_path, progress)

    while temperature > args.thermal_resume_temperature:
        time.sleep(args.thermal_poll_seconds)
        temperature = gpu_temperature_c()
        progress["thermal_poll_count"] += 1
        progress["maximum_runner_observed_temperature_c"] = max(
            float(progress["maximum_runner_observed_temperature_c"]),
            temperature,
        )
        progress["thermal_pause_seconds"] += time.perf_counter() - pause_started
        pause_started = time.perf_counter()
        atomic_json(progress_path, progress)

    append_jsonl(
        events_path,
        {
            "event": "thermal_pause_end",
            "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "temperature_c": temperature,
            "cumulative_thermal_pause_seconds": progress["thermal_pause_seconds"],
        },
    )


def extract_probability(payload: dict[str, Any]) -> float | None:
    probabilities = payload.get("probs")
    if not isinstance(probabilities, list):
        probabilities = payload.get("completion_probabilities")
    if isinstance(probabilities, list) and probabilities:
        first = probabilities[0]
        if isinstance(first, dict):
            value = first.get("prob")
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                return float(value)
            value = first.get("logprob")
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                return math.exp(float(value))
            candidates = first.get("probs")
            if isinstance(candidates, list) and candidates:
                candidate = candidates[0]
                if isinstance(candidate, dict):
                    for key in ("prob", "probability"):
                        value = candidate.get(key)
                        if isinstance(value, (int, float)) and math.isfinite(float(value)):
                            return float(value)
    return None


def audit_one(
    base_url: str,
    prompt_record: dict[str, str],
    audit_index: int,
    request_timeout: float,
) -> dict[str, Any]:
    started = time.perf_counter()
    response = http_json(
        f"{base_url}/completion",
        {
            "prompt": prompt_record["prompt"],
            "n_predict": 1,
            "temperature": 0.0,
            "top_k": 1,
            "n_probs": 1,
            "cache_prompt": False,
            "return_tokens": True,
            "seed": audit_index,
        },
        timeout=request_timeout,
    )
    latency = time.perf_counter() - started
    probability = extract_probability(response)
    audit_record = {
        "audit_index": audit_index,
        "row_id": prompt_record["row_id"],
        "prompt_sha256": prompt_record["prompt_sha256"],
        "content": str(response.get("content", "")),
        "tokens": response.get("tokens"),
        "probability": probability,
        "stop": bool(response.get("stop", False)),
    }
    digest = hashlib.sha256(canonical_bytes(audit_record)).digest()
    return {
        "digest128": int.from_bytes(digest[:16], "big"),
        "latency_seconds": latency,
        "probability": probability,
        "content_length": len(audit_record["content"]),
    }


def initial_progress(args: argparse.Namespace, manifest_hash: str) -> dict[str, Any]:
    return {
        "schema_version": "qwen08_completion_audit_progress_v0_2",
        "run_id": args.run_id,
        "audit_target": args.audit_count,
        "completed_audits": 0,
        "completed_chunks": 0,
        "cumulative_seconds": 0.0,
        "digest_sum_mod_128": "0",
        "digest_xor_128": "0",
        "probability_count": 0,
        "probability_sum": 0.0,
        "probability_sum_squares": 0.0,
        "latency_sum_seconds": 0.0,
        "latency_min_seconds": None,
        "latency_max_seconds": None,
        "content_bytes": 0,
        "thermal_pause_count": 0,
        "thermal_pause_seconds": 0.0,
        "thermal_poll_count": 0,
        "maximum_runner_observed_temperature_c": 0.0,
        "prompt_manifest_sha256": manifest_hash,
    }


def run(args: argparse.Namespace) -> None:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "events.jsonl"
    progress_path = output_dir / "progress.json"
    summary_path = output_dir / "summary.json"
    server_stdout_path = output_dir / "llama_server_stdout.log"
    server_stderr_path = output_dir / "llama_server_stderr.log"
    if summary_path.exists():
        print(summary_path.read_text(encoding="utf-8"))
        return

    prompts = load_prompts(args.prompt_manifest)
    manifest_hash = sha256(args.prompt_manifest)
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8-sig"))
        if progress["run_id"] != args.run_id or progress["audit_target"] != args.audit_count:
            raise ValueError("existing progress does not match the requested run")
        if progress["prompt_manifest_sha256"] != manifest_hash:
            raise ValueError("prompt manifest hash changed since the checkpoint")
    else:
        progress = initial_progress(args, manifest_hash)
        atomic_json(progress_path, progress)
    progress.setdefault("thermal_pause_count", 0)
    progress.setdefault("thermal_pause_seconds", 0.0)
    progress.setdefault("thermal_poll_count", 0)
    progress.setdefault("maximum_runner_observed_temperature_c", 0.0)

    if port_is_open(args.host, args.port):
        raise RuntimeError(f"registered server port {args.port} is already occupied")

    server_command = [
        str(args.server_path.resolve()),
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--model",
        str(args.model_path.resolve()),
        "--ctx-size",
        str(args.context_size),
        "--batch-size",
        str(args.batch_size),
        "--ubatch-size",
        str(args.ubatch_size),
        "--n-gpu-layers",
        str(args.gpu_layers),
        "--threads",
        str(args.threads),
        "--threads-batch",
        str(args.threads),
        "--parallel",
        str(args.parallel),
        "--cache-ram",
        "0",
        "--no-webui",
        "--no-warmup",
    ]
    append_jsonl(
        events_path,
        {
            "event": "runner_start",
            "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": args.run_id,
            "resuming_from": progress["completed_audits"],
            "server_command": server_command,
        },
    )
    base_url = f"http://{args.host}:{args.port}"
    server_process: subprocess.Popen[Any] | None = None
    server_stdout = server_stdout_path.open("ab")
    server_stderr = server_stderr_path.open("ab")
    try:
        server_process = subprocess.Popen(
            server_command,
            stdout=server_stdout,
            stderr=server_stderr,
            stdin=subprocess.DEVNULL,
        )
        wait_for_server(base_url, server_process, args.startup_timeout)
        append_jsonl(
            events_path,
            {
                "event": "server_ready",
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "server_pid": server_process.pid,
            },
        )

        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            warmup_records = [
                prompts[index % len(prompts)] for index in range(args.warmup_count)
            ]
            warmup_start = 0
            while warmup_start < len(warmup_records):
                wait_for_thermal_window(
                    args,
                    events_path,
                    progress_path,
                    progress,
                )
                warmup_end = min(
                    len(warmup_records),
                    warmup_start + min(args.thermal_check_every, args.parallel),
                )
                list(
                    executor.map(
                        lambda item: audit_one(
                            base_url, item[1], item[0], args.request_timeout
                        ),
                        enumerate(
                            warmup_records[warmup_start:warmup_end],
                            start=warmup_start,
                        ),
                    )
                )
                warmup_start = warmup_end

            completed = int(progress["completed_audits"])
            run_started = time.perf_counter()
            while completed < args.audit_count:
                chunk_end = min(args.audit_count, completed + args.checkpoint_every)
                results: list[dict[str, Any]] = []
                mini_start = completed
                while mini_start < chunk_end:
                    wait_for_thermal_window(
                        args,
                        events_path,
                        progress_path,
                        progress,
                    )
                    mini_end = min(
                        chunk_end,
                        mini_start + args.thermal_check_every,
                    )
                    work = [
                        (index, prompts[index % len(prompts)])
                        for index in range(mini_start, mini_end)
                    ]
                    results.extend(
                        executor.map(
                            lambda item: audit_one(
                                base_url, item[1], item[0], args.request_timeout
                            ),
                            work,
                        )
                    )
                    mini_start = mini_end

                digest_sum = int(progress["digest_sum_mod_128"])
                digest_xor = int(progress["digest_xor_128"])
                for result in results:
                    digest_sum = (digest_sum + int(result["digest128"])) % MODULUS
                    digest_xor ^= int(result["digest128"])
                    probability = result["probability"]
                    if probability is not None:
                        progress["probability_count"] += 1
                        progress["probability_sum"] += probability
                        progress["probability_sum_squares"] += probability * probability
                    latency = float(result["latency_seconds"])
                    progress["latency_sum_seconds"] += latency
                    progress["latency_min_seconds"] = (
                        latency
                        if progress["latency_min_seconds"] is None
                        else min(float(progress["latency_min_seconds"]), latency)
                    )
                    progress["latency_max_seconds"] = (
                        latency
                        if progress["latency_max_seconds"] is None
                        else max(float(progress["latency_max_seconds"]), latency)
                    )
                    progress["content_bytes"] += int(result["content_length"])
                progress["digest_sum_mod_128"] = str(digest_sum)
                progress["digest_xor_128"] = str(digest_xor)
                completed = chunk_end
                progress["completed_audits"] = completed
                progress["completed_chunks"] += 1
                progress["cumulative_seconds"] += time.perf_counter() - run_started
                run_started = time.perf_counter()
                progress["audits_per_second"] = (
                    completed / progress["cumulative_seconds"]
                    if progress["cumulative_seconds"] > 0
                    else None
                )
                atomic_json(progress_path, progress)
                append_jsonl(
                    events_path,
                    {
                        "event": "checkpoint",
                        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        **progress,
                    },
                )

        probability_count = int(progress["probability_count"])
        probability_mean = (
            progress["probability_sum"] / probability_count if probability_count else None
        )
        probability_variance = (
            max(
                0.0,
                progress["probability_sum_squares"] / probability_count
                - probability_mean * probability_mean,
            )
            if probability_count
            else None
        )
        summary = {
            "schema_version": "qwen08_completion_audit_summary_v0_1",
            "run_id": args.run_id,
            "status": "completed",
            "measurement_contract": {
                "unit": "one frozen-manifest prompt plus one deterministic next-token evaluation",
                "model": str(args.model_path.resolve()),
                "precision": "Q4_K_M",
                "generation_tokens": 1,
                "gradients": False,
                "weights_modified": False,
                "scientific_gate": False,
            },
            "counts": {
                "audits_completed": progress["completed_audits"],
                "unique_prompts": len(prompts),
                "chunks_completed": progress["completed_chunks"],
                "probability_scores_returned": probability_count,
                "content_bytes": progress["content_bytes"],
            },
            "timing": {
                "cumulative_seconds": progress["cumulative_seconds"],
                "audits_per_second": progress["audits_per_second"],
                "mean_request_latency_seconds": (
                    progress["latency_sum_seconds"] / progress["completed_audits"]
                ),
                "minimum_request_latency_seconds": progress["latency_min_seconds"],
                "maximum_request_latency_seconds": progress["latency_max_seconds"],
                "thermal_pause_count": progress["thermal_pause_count"],
                "thermal_pause_seconds": progress["thermal_pause_seconds"],
                "thermal_poll_count": progress["thermal_poll_count"],
                "maximum_runner_observed_temperature_c": progress[
                    "maximum_runner_observed_temperature_c"
                ],
            },
            "audit_statistics": {
                "returned_token_probability_mean": probability_mean,
                "returned_token_probability_variance": probability_variance,
                "digest_sum_mod_128": progress["digest_sum_mod_128"],
                "digest_xor_128": progress["digest_xor_128"],
            },
            "inputs": {
                "prompt_manifest": str(args.prompt_manifest.resolve()),
                "prompt_manifest_sha256": manifest_hash,
                "runner_sha256": sha256(Path(__file__).resolve()),
            },
            "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "claim_boundary": (
                "Model-forward completion audit proxy only; repeated prompts are not "
                "independent evidence and this run is not an ASMP-8 scientific gate."
            ),
        }
        atomic_json(summary_path, summary)
        append_jsonl(
            events_path,
            {"event": "complete", "summary_sha256": sha256(summary_path)},
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        if server_process is not None and server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait(timeout=15)
        server_stdout.close()
        server_stderr.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--server-path", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--audit-count", type=int, required=True)
    parser.add_argument("--checkpoint-every", type=int, default=1000)
    parser.add_argument("--warmup-count", type=int, default=8)
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--context-size", type=int, default=768)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--ubatch-size", type=int, default=256)
    parser.add_argument("--gpu-layers", type=int, default=99)
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8818)
    parser.add_argument("--startup-timeout", type=float, default=180.0)
    parser.add_argument("--request-timeout", type=float, default=120.0)
    parser.add_argument("--thermal-pause-temperature", type=float, default=0.0)
    parser.add_argument("--thermal-resume-temperature", type=float, default=0.0)
    parser.add_argument("--thermal-check-every", type=int, default=20)
    parser.add_argument("--thermal-poll-seconds", type=float, default=5.0)
    args = parser.parse_args()
    if args.audit_count <= 0 or args.checkpoint_every <= 0:
        parser.error("audit-count and checkpoint-every must be positive")
    if args.parallel <= 0 or args.warmup_count < 0:
        parser.error("parallel must be positive and warmup-count non-negative")
    if args.thermal_check_every <= 0 or args.thermal_poll_seconds <= 0:
        parser.error("thermal-check-every and thermal-poll-seconds must be positive")
    if args.thermal_pause_temperature > 0 and not (
        0 <= args.thermal_resume_temperature < args.thermal_pause_temperature
    ):
        parser.error(
            "thermal-resume-temperature must be non-negative and below "
            "thermal-pause-temperature"
        )
    if args.audit_count % args.checkpoint_every:
        parser.error("audit-count must be divisible by checkpoint-every")
    return args


if __name__ == "__main__":
    run(parse_args())
