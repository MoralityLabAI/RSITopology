from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

from joint_approximate import (
    build_joint_certificate,
    certificate_support,
    dot,
    evaluate_policy_family,
    fraction_text,
    identity,
    matmul,
    measurement_from_sources,
    q,
    quotient_analysis_map,
    realized_direction_audit,
    support_witness,
    vector_subtract,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def peak_resident_bytes() -> int:
    if os.name == "nt":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(Counters)
        if not ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        ):
            raise OSError("GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(usage * 1024)


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_text(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    return value


def load_fraction_fixture(raw: dict[str, Any]) -> dict[str, Any]:
    return jsonable_to_fraction(raw)


def jsonable_to_fraction(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: jsonable_to_fraction(item) for key, item in value.items()}
    if isinstance(value, list):
        return tuple(jsonable_to_fraction(item) for item in value)
    if isinstance(value, str):
        try:
            return q(value)
        except (ValueError, ZeroDivisionError):
            return value
    return value


def build_from_raw(raw: dict[str, Any]):
    return build_joint_certificate(
        raw["nominal_design"],
        raw["context_design"],
        raw["localized_values"],
        raw["localization_widths"],
        raw["midpoint_residual_widths"],
        raw["mechanical_row_l1_widths"],
        raw["semantic_incidence"],
        raw["semantic_cell_widths"],
    )


def scalar_decision(value: Fraction, width: Fraction) -> tuple[dict, dict]:
    certificate = build_joint_certificate(
        ((1,), (-1,)),
        ((), ()),
        (value, -value),
        (width, width),
        (0, 0),
        (0, 0),
        ((), ()),
        (),
    )
    return certificate, evaluate_policy_family(certificate, ((0,), (1,)))


def source_ablation(kind: str, amplitude: Fraction) -> dict[str, Any]:
    design = ((1,), (-1,))
    context = ((), ())
    theta = (Fraction(1),)
    delta = ((0,), (0,))
    localization = (Fraction(0), Fraction(0))
    midpoint = (Fraction(0), Fraction(0))
    semantic_incidence = ((), ())
    semantic_residual = ()
    localization_widths = (Fraction(0), Fraction(0))
    midpoint_widths = (Fraction(0), Fraction(0))
    mechanical_widths = (Fraction(0), Fraction(0))
    semantic_widths = ()
    if kind == "mechanical":
        delta = ((amplitude,), (-amplitude,))
        mechanical_widths = (amplitude, amplitude)
    elif kind == "localization":
        localization = (amplitude, -amplitude)
        localization_widths = (amplitude, amplitude)
    elif kind == "midpoint":
        midpoint = (amplitude, -amplitude)
        midpoint_widths = (amplitude, amplitude)
    elif kind == "semantic":
        semantic_incidence = ((1,), (-1,))
        semantic_residual = (amplitude,)
        semantic_widths = (amplitude,)
    else:
        raise ValueError(kind)
    values = measurement_from_sources(
        design,
        context,
        theta,
        (),
        delta,
        localization,
        midpoint,
        semantic_incidence,
        semantic_residual,
    )
    full = build_joint_certificate(
        design,
        context,
        values,
        localization_widths,
        midpoint_widths,
        mechanical_widths,
        semantic_incidence,
        semantic_widths,
    )
    ablated = build_joint_certificate(
        design,
        context,
        values,
        (0, 0),
        (0, 0),
        (0, 0),
        ((), ()),
        (),
    )
    realized = abs(full["theta_hat"][0] - theta[0])
    full_support = certificate_support(full, (1,))
    ablated_support = certificate_support(ablated, (1,))
    return {
        "ablated_support": ablated_support,
        "full_support": full_support,
        "full_support_covers": realized <= full_support,
        "omission_exposes_error": realized > ablated_support,
        "realized_error": realized,
        "source": kind,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    started_at = utc_now()
    start = time.perf_counter()

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    registration_hash = sha256(args.registration)
    for relative, expected in registration["sealed_files"].items():
        actual = sha256(REPO / relative)
        if actual != expected:
            raise RuntimeError(f"sealed source mismatch: {relative}")
    protocol_path = REPO / registration["protocol_path"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol["protocol_id"] != "ASMP-9-JOINT-APPROXIMATE-v0.31":
        raise RuntimeError("protocol mismatch")

    primary = load_fraction_fixture(protocol["primary_fixture"])
    localized = measurement_from_sources(
        primary["nominal_design"],
        primary["context_design"],
        primary["theta"],
        primary["context_parameter"],
        primary["mechanical_delta"],
        primary["localization_error"],
        primary["midpoint_residual"],
        primary["semantic_incidence"],
        primary["semantic_residual"],
    )
    certificate = build_joint_certificate(
        primary["nominal_design"],
        primary["context_design"],
        localized,
        primary["localization_widths"],
        primary["midpoint_residual_widths"],
        primary["mechanical_row_l1_widths"],
        primary["semantic_incidence"],
        primary["semantic_cell_widths"],
    )
    directions = primary["directions"]
    audits = realized_direction_audit(
        certificate, primary["theta"], directions
    )
    policy = evaluate_policy_family(certificate, primary["policies"])
    witness = support_witness(certificate, primary["support_direction"])

    controls = {
        key: load_fraction_fixture(value)
        for key, value in protocol["controls"].items()
    }
    rank_control = quotient_analysis_map(
        controls["context_confounding"]["nominal_design"],
        controls["context_confounding"]["context_design"],
    )
    mechanical_boundary = build_from_raw(controls["mechanical_boundary"])
    semantic_cancellation = build_from_raw(controls["semantic_cancellation"])
    semantic_support = certificate_support(semantic_cancellation, (1,))
    naive_semantic_support = Fraction(1, 5)
    anisotropic = build_from_raw(controls["anisotropic"])
    anisotropic_policy = evaluate_policy_family(
        anisotropic, controls["anisotropic"]["policies"]
    )
    anisotropic_margin = anisotropic_policy["margin_rows"][0]["margin"]
    anisotropic_support = anisotropic_policy["margin_rows"][0][
        "worst_case_margin_loss"
    ]
    isotropic_radius = max(
        certificate_support(anisotropic, direction)
        for direction in identity(2)
    )

    equality_raw = load_fraction_fixture(
        protocol["decision_controls"]["equality"]
    )
    equality_certificate, equality_policy = scalar_decision(
        equality_raw["localized_value"],
        equality_raw["localization_width"],
    )
    risk_raw = load_fraction_fixture(protocol["decision_controls"]["risk"])
    risk_certificate, risk_policy = scalar_decision(
        risk_raw["localized_value"], risk_raw["localization_width"]
    )
    risk_selected = risk_policy["selected_policy"]
    risk_occupancies = ((0,), (1,))
    true_values = tuple(
        dot(row, (risk_raw["true_theta_witness"],))
        for row in risk_occupancies
    )
    risk_actual_regret = max(true_values) - true_values[risk_selected]

    erasure_theta_0 = measurement_from_sources(
        ((1,),),
        ((),),
        (0,),
        (),
        ((-1,),),
        (0,),
        (0,),
        ((),),
        (),
    )
    erasure_theta_37 = measurement_from_sources(
        ((1,),),
        ((),),
        (37,),
        (),
        ((-1,),),
        (0,),
        (0,),
        ((),),
        (),
    )

    amplitude = q(protocol["source_ablation_amplitude"])
    ablations = tuple(
        source_ablation(kind, amplitude)
        for kind in ("mechanical", "localization", "midpoint", "semantic")
    )

    prior_text = (
        (HERE / "PRIOR_ART_GATE_v0_31.md").read_text(encoding="utf-8")
        + (HERE / "THEOREM_DRAFT_v0_31.md").read_text(encoding="utf-8")
    ).lower()
    prior_tokens = (
        "frisch",
        "el ghaoui",
        "set-membership",
        "support function",
        "abbeel",
        "iyengar",
        "nilim",
        "novelty is not claimed",
        "does not",
        "resolve asmp-9",
    )
    elapsed = time.perf_counter() - start
    peak = peak_resident_bytes()

    gates = {
        "G0_registration_binding": True,
        "G1_context_projection": (
            certificate["projected_rank"] == 3
            and matmul(
                certificate["analysis_map"], primary["nominal_design"]
            )
            == identity(3)
            and all(
                value == 0
                for row in matmul(
                    certificate["analysis_map"], primary["context_design"]
                )
                for value in row
            )
            and rank_control["status"] == "context_confounded"
        ),
        "G2_joint_source_coverage": (
            len(audits) == 7 and all(row["covered"] for row in audits)
        ),
        "G3_mechanical_contraction": (
            certificate["mechanical_gain"] < 1
            and mechanical_boundary["mechanical_gain"] == 1
            and mechanical_boundary["status"]
            == "mechanical_contraction_unavailable"
            and erasure_theta_0 == erasure_theta_37 == (0,)
        ),
        "G4_semantic_incidence": (
            semantic_support == 0 and naive_semantic_support > 0
        ),
        "G5_support_sharpness": (
            witness["attained_support"]
            == certificate_support(certificate, primary["support_direction"])
        ),
        "G6_policy_handoff": (
            policy["policy_identity_certified"]
            and policy["robust_regret_bound"] == 0
            and not equality_policy["policy_identity_certified"]
            and equality_policy["margin_rows"][0]["lower_margin"] == 0
            and risk_policy["robust_regret_bound"] == risk_actual_regret
            and risk_actual_regret == Fraction(9, 10)
        ),
        "G7_source_ablation": (
            len(ablations) == 4
            and all(
                row["full_support_covers"]
                and row["omission_exposes_error"]
                for row in ablations
            )
        ),
        "G8_shape_advantage": (
            anisotropic_policy["policy_identity_certified"]
            and anisotropic_support < anisotropic_margin
            and isotropic_radius >= anisotropic_margin
        ),
        "G9_context_rank_no_go": (
            not rank_control["available"]
            and rank_control["projected_rank"] == 0
        ),
        "G10_prior_art_and_claim_boundary": all(
            token in prior_text for token in prior_tokens
        ),
        "G11_resource_and_scope": (
            elapsed <= protocol["resource_caps"]["wall_seconds"]
            and peak <= protocol["resource_caps"]["peak_resident_bytes"]
            and not protocol["resource_caps"]["gpu_allowed"]
        ),
    }
    verdict = (
        "joint_approximate_boundary_established_v0_31"
        if all(gates.values())
        else "joint_approximate_boundary_not_established_v0_31"
    )
    result = {
        "controls": {
            "anisotropic": {
                "isotropic_radius": isotropic_radius,
                "margin": anisotropic_margin,
                "policy": anisotropic_policy,
                "zonotope_support": anisotropic_support,
            },
            "context_confounding": rank_control,
            "mechanical_boundary": {
                "erasure_observation_theta_0": erasure_theta_0[0],
                "erasure_observation_theta_37": erasure_theta_37[0],
                "mechanical_gain": mechanical_boundary["mechanical_gain"],
                "status": mechanical_boundary["status"],
            },
            "semantic_cancellation": {
                "naive_independent_support": naive_semantic_support,
                "structured_support": semantic_support,
            },
        },
        "decision_controls": {
            "equality": equality_policy,
            "risk": {
                "actual_regret": risk_actual_regret,
                "certificate": risk_certificate,
                "policy": risk_policy,
            },
        },
        "gates": {
            name: {"pass": passed}
            for name, passed in sorted(gates.items())
        },
        "primary": {
            "certificate": certificate,
            "direction_audits": audits,
            "localized_values": localized,
            "policy": policy,
            "support_witness": witness,
            "true_theta": primary["theta"],
        },
        "protocol_id": protocol["protocol_id"],
        "resource": {
            "gpu_used": False,
            "peak_resident_bytes": peak,
            "wall_seconds": elapsed,
        },
        "source_ablations": ablations,
        "verdict": verdict,
    }
    result = jsonable(result)
    result_path = args.output_dir / "result_v0_31.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "finished_at_utc": utc_now(),
        "implementation_commit": registration["implementation_commit"],
        "protocol_sha256": sha256(protocol_path),
        "registered_at_utc": registration["registered_at_utc"],
        "registration_sha256": registration_hash,
        "result_sha256": sha256(result_path),
        "run_commit": git("rev-parse", "HEAD"),
        "started_at_utc": started_at,
        "verdict": verdict,
    }
    write_json_exclusive(args.output_dir / "run_receipt_v0_31.json", receipt)
    print(json.dumps({"gates": gates, "receipt": receipt}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
