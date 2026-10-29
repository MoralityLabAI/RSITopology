import json
import time
from pathlib import Path

from run_v0_2_2 import RSSMonitor


HERE = Path(__file__).resolve().parent


def test_resource_amendment_binds_both_parents():
    import run as parent

    amendment = json.loads((HERE / "protocol_v0_2_2.json").read_text(encoding="utf-8"))
    assert parent.sha256_file(HERE / amendment["scientific_parent_protocol"]) == amendment["scientific_parent_sha256"]
    assert parent.sha256_file(HERE / amendment["performance_parent_amendment"]) == amendment["performance_parent_sha256"]
    assert amendment["scientific_contract_changes"] == "none"


def test_rss_monitor_reports_positive_process_memory_and_stops():
    monitor = RSSMonitor(interval_seconds=0.001)
    monitor.start()
    payload = bytearray(1024 * 1024)
    time.sleep(0.005)
    peak = monitor.stop()
    assert payload[0] == 0
    assert peak > 0
    assert not monitor.thread.is_alive()


def test_operational_ceiling_leaves_external_shutdown_margin():
    amendment = json.loads((HERE / "protocol_v0_2_2.json").read_text(encoding="utf-8"))
    limits = amendment["resource_measurement"]
    assert limits["operational_wall_ceiling_seconds"] == 150
    assert limits["external_total_wall_ceiling_seconds"] == 180
    assert limits["external_total_wall_ceiling_seconds"] - limits["operational_wall_ceiling_seconds"] == 30
