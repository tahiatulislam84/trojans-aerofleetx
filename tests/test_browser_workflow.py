import contextlib
import http.server
import socket
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'app/src/main/assets/web'


def free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def local_server():
    port = free_port()
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(WEB), **kw)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{port}/index.html'
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.browser
def test_integrated_browser_workflow():
    with local_server() as url, sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1080, 'height': 1920})
        errors = []
        page.on('pageerror', lambda exc: errors.append(str(exc)))
        page.goto(url, wait_until='networkidle')
        page.wait_for_selector('#app:not(.hidden)')

        assert page.locator('#app').is_visible()
        assert page.locator('#fleetAircraftGrid .fleet-aircraft-card').count() == 4
        assert page.locator('#fleetHealth').inner_text().endswith('%')

        page.wait_for_selector('#tutorialSheet:not(.hidden)')
        page.get_by_role('button', name='Close tutorial', exact=True).click()
        assert page.locator('#tutorialSheet').is_hidden()

        page.evaluate("openScreen('predictive')")
        assert page.locator('#predictive').is_visible()
        assert page.locator('#predictiveComponentList .predictive-component').count() >= 4
        assert 'warning' in page.locator('#predictiveComponentList').inner_text().lower()

        page.locator('#schedulePredictiveBtn').click()
        assert page.locator('#scheduleModal').is_visible()
        page.evaluate("hideSheet('scheduleModal')")

        page.evaluate("openScreen('schedule')")
        assert page.locator('#schedule').is_visible()
        page.evaluate("openScreen('xr')")
        assert page.locator('#xr').is_visible()
        page.evaluate("openScreen('training')")
        assert page.locator('#training').is_visible()
        page.evaluate("openScreen('safety')")
        assert page.locator('#safety').is_visible()
        assert 'research' in page.locator('#safety').inner_text().lower()
        assert errors == []
        browser.close()
