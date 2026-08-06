from __future__ import annotations

import contextlib
import http.server
import json
import socket
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'app/src/main/assets/web'
OUT = ROOT / 'validation/browser_validation_latest.json'


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


def add(checks, name, passed, detail=''):
    checks.append({'name': name, 'pass': bool(passed), 'detail': detail})


def main():
    started = time.perf_counter()
    checks, errors = [], []
    with local_server() as url, sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1080, 'height': 1920})
        page.on('pageerror', lambda exc: errors.append(str(exc)))
        page.goto(url, wait_until='networkidle')
        page.wait_for_selector('#app:not(.hidden)')
        add(checks, 'app visible', page.locator('#app').is_visible())
        add(checks, 'fleet aircraft rendered', page.locator('#fleetAircraftGrid .fleet-aircraft-card').count() == 4)
        add(checks, 'fleet health value', page.locator('#fleetHealth').inner_text().endswith('%'))
        page.evaluate("openScreen('predictive')")
        add(checks, 'predictive visible', page.locator('#predictive').is_visible())
        add(checks, 'component cards', page.locator('#predictiveComponentList .predictive-component').count() >= 4)
        add(checks, 'explainability shown', 'warning' in page.locator('#predictiveComponentList').inner_text().lower())
        page.locator('#schedulePredictiveBtn').click()
        add(checks, 'schedule modal opens', page.locator('#scheduleModal').is_visible())
        page.evaluate("hideSheet('scheduleModal')")
        page.evaluate("openScreen('schedule')")
        add(checks, 'mission control opens', page.locator('#schedule').is_visible())
        page.evaluate("openScreen('xr')")
        add(checks, 'xr opens', page.locator('#xr').is_visible())
        page.evaluate("openScreen('training')")
        add(checks, 'training opens', page.locator('#training').is_visible())
        page.evaluate("openScreen('safety')")
        add(checks, 'safety opens', page.locator('#safety').is_visible())
        add(checks, 'research boundary present', 'research' in page.locator('#safety').inner_text().lower())
        browser.close()
    result = {
        'duration_seconds': round(time.perf_counter() - started, 3),
        'checks': checks,
        'javascript_errors': errors,
        'pass': all(c['pass'] for c in checks) and not errors,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['pass'] else 1)


if __name__ == '__main__':
    main()
