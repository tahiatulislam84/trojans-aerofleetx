import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'app/src/main/assets/web'
APP_JS = (WEB / 'app.js').read_text(encoding='utf-8')
INDEX = (WEB / 'index.html').read_text(encoding='utf-8')
MANIFEST = (ROOT / 'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
GRADLE = (ROOT / 'app/build.gradle.kts').read_text(encoding='utf-8')


class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get('id'):
            self.ids.append(data['id'])


def test_javascript_files_exist_and_are_nonempty():
    assert (WEB / 'app.js').stat().st_size > 50_000
    assert (WEB / 'xr3d.js').stat().st_size > 1_000


def test_no_duplicate_html_ids():
    parser = IdParser()
    parser.feed(INDEX)
    assert len(parser.ids) == len(set(parser.ids))
    assert len(parser.ids) >= 150


def test_permanent_package_and_api_levels():
    assert 'namespace = "com.trojans.aerofleetx.mobileapp"' in GRADLE
    assert 'applicationId = "com.trojans.aerofleetx.mobileapp"' in GRADLE
    assert re.search(r'compileSdk\s*=\s*36', GRADLE)
    assert re.search(r'targetSdk\s*=\s*36', GRADLE)
    assert re.search(r'minSdk\s*=\s*23', GRADLE)


def test_production_manifest_security_controls():
    assert 'android.permission.INTERNET' not in MANIFEST
    assert 'android:usesCleartextTraffic="false"' in MANIFEST
    assert 'android:allowBackup="false"' in MANIFEST


def test_research_boundary_present():
    lower = (APP_JS + INDEX).lower()
    assert 'research' in lower
    assert 'release-to-service' in lower
    assert 'approved maintenance' in lower or 'approved operator' in lower


def test_digital_twin_not_used_as_navigation_claim():
    assert 'Fleet & Digital Twin' not in INDEX
    assert "demos:['Fleet & Digital Twin'" not in APP_JS
    assert 'Fleet & Digital Aircraft' in INDEX


def test_check_letter_does_not_auto_escalate_priority():
    assert "priority:selectedCheckType==='D'?'Critical'" not in APP_JS
    assert "priority:selectedCheckType==='C'||selectedCheckType==='D'?'High'" not in APP_JS
    assert 'Check type does not determine operational priority' in APP_JS


def test_predictive_profiles_and_aircraft_counts():
    aircraft_ids = re.findall(r"'((?:DEMO-B(?:737|777|787)-01)|TRAINING-C130J-01)'\s*:\s*\[", APP_JS)
    assert sorted(set(aircraft_ids)) == sorted([
        'DEMO-B737-01', 'DEMO-B777-01', 'DEMO-B787-01', 'TRAINING-C130J-01'
    ])
    predictive_section = APP_JS.split('const predictiveTemplates=', 1)[1].split('function predictiveStore()', 1)[0]
    component_ids = re.findall(r"\{id:'(?:b777|b737|b787|c130)-[^']+'", predictive_section)
    assert len(component_ids) == 18
    assert "state.profile==='routine'" in APP_JS
    assert "state.profile==='degrading'" in APP_JS
    assert "predictiveProfile='c-check'" in APP_JS


def test_risk_thresholds_are_explicit_and_bounded():
    assert 'function predictiveRisk(c)' in APP_JS
    assert "return Math.max(0,Math.min(100,Math.round(r)))" in APP_JS
    assert "return r>=70?'High':r>=45?'Medium':'Low'" in APP_JS


def test_recorded_validation_is_machine_readable():
    browser = json.loads((ROOT / 'validation/browser_validation_v1.0.json').read_text())
    build = json.loads((ROOT / 'validation/build_validation_v1.0.json').read_text())
    assert browser['pass'] is True
    assert len(browser['checks']) == 12
    assert all(item['pass'] for item in browser['checks'])
    assert browser['javascript_errors'] == []
    assert len(browser['screenshots']) == 6
    assert build['aab_signed_verified'] is True
    assert build['apk_signed_verified'] is True
    assert build['target_sdk'] == 36


def test_android_java_export_exception_contract():
    java = (ROOT / 'app/src/main/java/com/trojans/aerofleetx/mobileapp/AeroInspectActivity.java').read_text(encoding='utf-8')
    method = java.split('private String writeExport', 1)[1].split('private String sanitizeFilename', 1)[0]
    assert 'catch (Exception error)' not in method
    assert 'catch (IOException error)' in method
    assert 'catch (RuntimeException error)' in method


def test_clean_build_ci_is_unsigned_and_pinned():
    workflow = (ROOT / '.github/workflows/android-ci.yml').read_text(encoding='utf-8')
    wrapper = (ROOT / 'gradle/wrapper/gradle-wrapper.properties').read_text(encoding='utf-8')
    assert 'clean lintDebug assembleDebug' in workflow
    assert 'AEROFLEETX_UPLOAD_KEYSTORE_BASE64' not in workflow
    assert 'java-version: "17"' in workflow
    assert 'platforms;android-36' in workflow
    assert 'android-actions/setup-android@v4' in workflow
    assert 'build-tools;35.0.0' in workflow
    assert 'actions/upload-artifact@v7' in workflow
    assert 'distributionSha256Sum=20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78' in wrapper
