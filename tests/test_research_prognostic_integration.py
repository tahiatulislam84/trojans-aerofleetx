from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "app" / "src" / "main" / "assets" / "web"
INDEX = WEB / "index.html"
APP = WEB / "app.js"
ADAPTER = WEB / "research-prognostic.js"
MAPPING = ROOT / "research" / "prognostics" / "rul-priority-mapping.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_experimental_adapter_is_loaded_without_replacing_demo_script():
    html = read(INDEX)
    assert '<script src="app.js"></script>' in html
    assert '<script src="research-prognostic.js"></script>' in html
    assert html.index('<script src="app.js"></script>') < html.index('<script src="research-prognostic.js"></script>')


def test_existing_deterministic_predictive_logic_is_preserved():
    app = read(APP)
    assert "function predictiveRisk(c)" in app
    assert "function predictiveLevel(r)" in app
    assert "function predictedCycles(r)" in app
    assert "r>=70?'High':r>=45?'Medium':'Low'" in app


def test_research_adapter_has_locked_rul_priority_boundaries():
    adapter = read(ADAPTER)
    assert "if(rul<=10)" in adapter
    assert "if(rul<=25)" in adapter
    assert "if(rul<=60)" in adapter
    assert "if(rul<=100)" in adapter
    assert "priority:'Low',reviewBand:'>100'" in adapter
    assert "priority:'Unavailable',reviewBand:'Unavailable'" in adapter


def test_research_adapter_preserves_provenance_and_limitations():
    adapter = read(ADAPTER)
    assert "cmapss-fd001-rf-phase5-v1" in adapter
    assert "NASA C-MAPSS FD001" in adapter
    assert "74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f" in adapter
    assert "346d8db1a7e51cdd05ae5dc206e953ec6402fac2" in adapter
    assert "EXPERIMENTAL RESEARCH OUTPUT" in adapter
    assert "optimistic RUL bias" in adapter
    assert "no airworthiness, release-to-service or operational maintenance authority" in adapter


def test_research_panel_has_no_operational_action_controls():
    adapter = read(ADAPTER)
    assert "This panel cannot create a work order, schedule maintenance" in adapter
    assert "createPredictiveWorkOrder(" not in adapter
    assert "schedulePredictiveInspection(" not in adapter
    assert "aircraftDailyCycles" not in adapter


def test_mapping_file_carries_research_only_boundary():
    mapping = read(MAPPING)
    assert '"status": "research-only"' in mapping
    assert '"priority": "Unavailable"' in mapping
    assert '"automatic work-order creation"' in mapping
    assert '"release-to-service decision"' in mapping
