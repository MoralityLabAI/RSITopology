from verify_construction_release_v0681 import verify


def test_construction_release_reproduces_and_closes_resources() -> None:
    result = verify()
    assert result["status"] == "passed"
    assert result["manifest_files_checked"] == 18
    assert result["records"] == 528
    assert result["semantic_inputs"] == 264
    assert result["scenarios"] == 12
    assert result["scenario_successes"] == 12
    assert result["decision"] == "local_and_global_confirmation_authorized"
