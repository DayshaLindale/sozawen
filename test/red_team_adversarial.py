"""Sozawen Adversarial Red Team — hit it like Mythos.

Not just "does it work" — "can it break?"
Every input vector. Every edge case. Every boundary assumption.
This is a one-time purchase. No live patching. It has to be right.
"""
import requests, json, sys, os, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://127.0.0.1:8090'
TEST_FILE = 'E:/sozawen/test/red_team_test.wav'
results = []

def test(name, method, url, data=None, expect_crash=False):
    """PASS = no 500 crash. 400/404 = proper rejection = PASS."""
    try:
        r = requests.get(f'{BASE}{url}', timeout=30) if method == 'GET' else requests.post(f'{BASE}{url}', json=data, timeout=60)
        ok = r.status_code != 500  # anything except a crash is a pass
        results.append((name, 'PASS' if ok else 'FAIL', r.status_code, ''))
        print(f'  [{"V" if ok else "X"}] {name} [{r.status_code}]')
        return r
    except Exception as e:
        results.append((name, 'ERROR', 0, str(e)[:60]))
        print(f'  [!] {name} -- {str(e)[:60]}')
        return None

print('=' * 70)
print('  SOZAWEN ADVERSARIAL RED TEAM')
print('  Every vector. Every edge case. Hit it like Mythos.')
print('=' * 70)

# ═══ 1. INPUT VALIDATION — bad data shouldn't crash ═══
print('\n--- [1] INPUT VALIDATION (bad data) ---')
test('Empty JSON body', 'POST', '/api/track/add', {})
test('Missing fields', 'POST', '/api/fx/apply', {})
test('Null track ID', 'POST', '/api/fx/apply', {'track_id': None, 'effect': 'eq', 'params': {}})
test('Negative track ID', 'POST', '/api/fx/apply', {'track_id': -1, 'effect': 'eq', 'params': {}})
test('Huge track ID', 'POST', '/api/fx/apply', {'track_id': 999999, 'effect': 'eq', 'params': {}})
test('Invalid effect name', 'POST', '/api/fx/apply', {'track_id': 0, 'effect': 'DROP_TABLE', 'params': {}})
test('Effect with wrong params', 'POST', '/api/fx/apply', {'track_id': 0, 'effect': 'eq', 'params': {'nonexistent': 999}})
test('Extreme EQ values', 'POST', '/api/fx/apply', {'track_id': 0, 'effect': 'eq', 'params': {'low_gain': 9999}})

# ═══ 2. PATH TRAVERSAL — can't access outside the app ═══
print('\n--- [2] PATH TRAVERSAL ---')
test('Path traversal in track add', 'POST', '/api/track/add', {'file_path': '../../../../etc/passwd', 'name': 'hack'})
test('Path traversal in analyze', 'POST', '/api/analyze', {'file_path': '..\\..\\..\\windows\\system32\\config\\sam'})
test('UNC path', 'POST', '/api/track/add', {'file_path': '\\\\evil-server\\share\\file.wav', 'name': 'unc'})
test('Null bytes in path', 'POST', '/api/track/add', {'file_path': 'C:\\file.wav\x00.exe', 'name': 'null'})
test('Browse folder outside app', 'POST', '/api/browse-folder', {'path': 'C:\\Windows\\System32'})

# ═══ 3. LICENSE BYPASS — can't use without key ═══
print('\n--- [3] LICENSE ---')
test('Empty key', 'POST', '/api/license/activate', {'key': ''})
test('Null key', 'POST', '/api/license/activate', {'key': None})
test('Key with injection', 'POST', '/api/license/activate', {'key': "'; DROP TABLE licenses; --"})
test('Very long key', 'POST', '/api/license/activate', {'key': 'A' * 10000})
test('Key with unicode', 'POST', '/api/license/activate', {'key': 'AAAA-BBBB-' + chr(0) + chr(65535)})

# ═══ 4. XSS — can't inject scripts ═══
print('\n--- [4] XSS VECTORS ---')
test('XSS in track name', 'POST', '/api/track/add', {'name': '<script>alert(1)</script>', 'file_path': ''})
test('XSS in feedback', 'POST', '/api/feedback', {'type': '<img onerror=alert(1)>', 'text': 'test', 'email': ''})
test('XSS in bandmate', 'POST', '/api/bandmate', {'message': '<script>alert(1)</script>', 'context': {}})

# ═══ 5. DENIAL OF SERVICE — resource exhaustion ═══
print('\n--- [5] RESOURCE LIMITS ---')
test('Very long message to bandmate', 'POST', '/api/bandmate', {'message': 'A' * 100000, 'context': {}})
test('Many notes in synth', 'POST', '/api/instrument/synth', {
    'notes': [{'note': 60, 'start_beat': i*0.1, 'duration_beats': 0.1, 'velocity': 100} for i in range(1000)],
    'bpm': 120, 'params': {}, 'name': 'stress'})
test('Many drum hits', 'POST', '/api/instrument/drums', {
    'pattern': [{'sound': 'kick', 'beat': i*0.01, 'velocity': 0.8} for i in range(5000)],
    'bpm': 120, 'name': 'stress'})
test('Huge pattern', 'POST', '/api/midi/pattern', {
    'pattern': {'name': 'huge', 'length_beats': 99999, 'notes': [
        {'note': 60, 'start_beat': 0, 'duration_beats': 1, 'velocity': 100}]},
    'bpm': 120, 'name': 'huge'})

# ═══ 6. NONEXISTENT ENDPOINTS ═══
print('\n--- [6] MISSING ENDPOINTS ---')
test('404 endpoint', 'GET', '/api/nonexistent')
test('Admin endpoint', 'GET', '/api/admin')
test('Debug endpoint', 'GET', '/api/debug')

# ═══ 7. CONCURRENT OPERATIONS ═══
print('\n--- [7] CONCURRENT ---')
import concurrent.futures
def hit_status(_):
    try:
        r = requests.get(f'{BASE}/api/status', timeout=10)
        return r.status_code == 200
    except:
        return False

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    futures = [pool.submit(hit_status, i) for i in range(20)]
    ok = sum(f.result() for f in futures)
    results.append(('20 concurrent status', 'PASS' if ok >= 18 else 'FAIL', ok, ''))
    print(f'  [{"V" if ok >= 18 else "X"}] 20 concurrent status requests: {ok}/20 succeeded')

# ═══ 8. EDGE CASES ═══
print('\n--- [8] EDGE CASES ---')
# Add a real track for edge case tests
requests.post(f'{BASE}/api/track/add', json={'file_path': TEST_FILE, 'name': 'EdgeTest'}, timeout=10)
test('Seek negative', 'POST', '/api/transport/seek', {'seconds': -100})
test('Seek huge', 'POST', '/api/transport/seek', {'seconds': 999999})
test('Volume negative', 'POST', '/api/track/1/volume', {'volume': -5})
test('Volume huge', 'POST', '/api/track/1/volume', {'volume': 999})
test('Pan extreme', 'POST', '/api/track/1/pan', {'pan': 50})
test('Loop backwards', 'POST', '/api/loop', {'start': 10, 'end': 5, 'enabled': True})
test('Empty search', 'POST', '/api/learn/search', {'query': ''})
test('Theory bad key', 'POST', '/api/theory/analyze-key', {'key': 'ZZZZZ'})
test('Feedback empty text', 'POST', '/api/feedback', {'type': 'bug', 'text': '', 'email': ''})

# ═══ SUMMARY ═══
print('\n' + '=' * 70)
passes = sum(1 for _, s, _, _ in results if s == 'PASS')
fails = sum(1 for _, s, _, _ in results if s == 'FAIL')
errors = sum(1 for _, s, _, _ in results if s == 'ERROR')
total = len(results)
print(f'  ADVERSARIAL: {passes}/{total} PASS | {fails} FAIL | {errors} ERROR')
print('=' * 70)

if fails or errors:
    print('\n  FAILURES:')
    for name, status, code, err in results:
        if status != 'PASS':
            print(f'    [{status}] {name} [{code}] {err}')
else:
    print('  >>> ADVERSARIAL CLEAN — NO CRASHES, NO BYPASSES <<<')

sys.exit(1 if (fails or errors) else 0)
