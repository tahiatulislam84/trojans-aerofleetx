import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "prognostics"


def test_research_protocol_files_exist():
    required = [
        "pipeline.py",
        "run_experiment.py",
        "verify_dataset.py",
        "protocol.json",
        "reference_results.json",
        "requirements.txt",
        "ENVIRONMENT.md",
        "README.md",
        "rul-priority-mapping.json",
    ]
    for name in required:
        assert (RESEARCH / name).is_file(), name


def test_raw_dataset_is_not_part_of_reproducibility_package():
    tracked_like = list(RESEARCH.glob("CMAPSSData.zip")) + list(RESEARCH.glob("data/**/*.zip"))
    assert tracked_like == []


def test_protocol_checksum_matches_phase3_record():
    protocol = json.loads((RESEARCH / "protocol.json").read_text(encoding="utf-8"))
    assert protocol["dataset"]["sha256"] == "74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f"
    assert protocol["dataset"]["raw_data_committed"] is False


def test_reference_results_are_explicitly_non_tuning_evidence():
    reference = json.loads((RESEARCH / "reference_results.json").read_text(encoding="utf-8"))
    assert "do not use for retuning" in reference["status"].lower()
    assert reference["phase6"]["optimistic_predictions"] == 79
    assert reference["phase7_priority_audit"]["under_prioritized"] == 26


def test_run_experiment_requires_explicit_flag_to_open_official_truth():
    source = (RESEARCH / "run_experiment.py").read_text(encoding="utf-8")
    assert "--evaluate-official-test" in source
    assert "include_test_truth=args.evaluate_official_test" in source


def test_documentation_keeps_operational_boundary():
    readme = (RESEARCH / "README.md").read_text(encoding="utf-8").lower()
    for phrase in [
        "not an airworthiness",
        "not commit",
        "official test",
        "no post-test retuning",
    ]:
        assert phrase in readme
