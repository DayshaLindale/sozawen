"""Sozawen Full Red Team — Every endpoint, every feature, no shortcuts."""
import requests, json, time, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://127.0.0.1:8090'
TEST_FILE = 'E:/sozawen/test/red_team_test.wav'
results = []

def test(name, method, url, data=None, expect_ok=True):
    try:
        if method == 'GET':
            r = requests.get(f'{BASE}{url}', timeout=60)
        else:
            r = requests.post(f'{BASE}{url}', json=data, timeout=120)
        body = r.json() if 'json' in r.headers.get('content-type', '') else {}
        err = body.get('error', '')
        ok = r.status_code == 200 and (not err if expect_ok else True)
        results.append((name, 'PASS' if ok else 'FAIL', r.status_code, err))
        sym = 'V' if ok else 'X'
        print(f'  [{sym}] {name}' + (f' -- {err}' if err else ''))
        return body
    except Exception as e:
        results.append((name, 'ERROR', 0, str(e)[:80]))
        print(f'  [!] {name} -- {str(e)[:80]}')
        return {}

print('=' * 70)
print('  SOZAWEN FULL RED TEAM')
print('  Every endpoint. Every feature. No shortcuts.')
print('=' * 70)

# 1. HEALTH
print('\n--- [1] HEALTH & STATIC ---')
test('API status', 'GET', '/api/status')
test('Context', 'GET', '/api/context')
test('Input devices', 'GET', '/api/input-devices')
test('Site HTML', 'GET', '/static/site.html')
test('DAW HTML', 'GET', '/static/index.html')
test('Favicon SVG', 'GET', '/static/favicon.svg')
test('Logo PNG', 'GET', '/static/logo.png')

# 2. LICENSE
print('\n--- [2] LICENSE ---')
test('License status', 'GET', '/api/license/status')
test('Activate bad key', 'POST', '/api/license/activate', {'key': 'FAKE'}, expect_ok=False)

# 3. TRACKS
print('\n--- [3] TRACK MANAGEMENT ---')
d = test('Add track + audio', 'POST', '/api/track/add', {'file_path': TEST_FILE, 'name': 'RT_Main'})
tid = d.get('track_id', 0)
print(f'       Track ID: {tid}')
test('Add empty track', 'POST', '/api/track/add', {'name': 'RT_Empty'})
test('Volume 75%', 'POST', f'/api/track/{tid}/volume', {'volume': 0.75})
test('Pan right', 'POST', f'/api/track/{tid}/pan', {'pan': 0.5})
test('Pan center', 'POST', f'/api/track/{tid}/pan', {'pan': 0.0})
test('Mute on', 'POST', f'/api/track/{tid}/mute')
test('Mute off', 'POST', f'/api/track/{tid}/mute')
test('Solo on', 'POST', f'/api/track/{tid}/solo')
test('Solo off', 'POST', f'/api/track/{tid}/solo')

# 4. WAVEFORM
print('\n--- [4] WAVEFORM ---')
d = test('Waveform 500px', 'GET', f'/api/waveform/{tid}?width=500')
pk = len(d.get('peaks', []))
print(f'       Peaks: {pk}')
if pk == 0:
    results.append(('Waveform has peaks', 'FAIL', 200, 'Zero'))
    print('  [X] Waveform has peaks')
else:
    results.append(('Waveform has peaks', 'PASS', 200, ''))
    print('  [V] Waveform has peaks')

d = test('Waveform 2000px', 'GET', f'/api/waveform/{tid}?width=2000')

# 5. TRANSPORT
print('\n--- [5] TRANSPORT ---')
test('Play', 'POST', '/api/transport/play')
time.sleep(0.3)
d = test('State playing', 'GET', '/api/transport/state')
playing = d.get('playing', False)
if not playing:
    results.append(('Is playing', 'FAIL', 200, 'not playing'))
else:
    results.append(('Is playing', 'PASS', 200, ''))
print(f'       Playing: {playing}, Pos: {d.get("position_seconds",0):.2f}s')
test('Seek 3s', 'POST', '/api/transport/seek', {'seconds': 3.0})
test('Pause', 'POST', '/api/transport/pause')
test('Stop', 'POST', '/api/transport/stop')
test('Seek 0', 'POST', '/api/transport/seek', {'seconds': 0})

# 6. CONTEXT
print('\n--- [6] CONTEXT ENGINE ---')
test('Action: drop_file', 'POST', '/api/context/action', {'action': 'drop_file'})
test('Action: select_region', 'POST', '/api/context/action', {'action': 'select_region'})
test('Action: adjust_volume', 'POST', '/api/context/action', {'action': 'adjust_volume'})
d = test('Context state', 'GET', '/api/context')
print(f'       Phase: {d.get("phase")}, Tools: {len(d.get("prominent_tools",[]))}+{len(d.get("available_tools",[]))}')

# 7. ALL 15 EFFECTS
print('\n--- [7] 15 AUDIO EFFECTS ---')
effects = [
    ('noise_gate', {'threshold_db': -40, 'attack_ms': 10, 'release_ms': 100}),
    ('eq', {'low_db': 2, 'low_mid_db': 0, 'mid_db': -1, 'high_mid_db': 1, 'high_db': 0}),
    ('compressor', {'threshold_db': -20, 'ratio': 3.0, 'attack_ms': 10, 'release_ms': 100, 'makeup_db': 0}),
    ('reverb', {'room_size': 0.4, 'decay': 1.5, 'wet_dry': 0.25}),
    ('delay', {'delay_ms': 375, 'feedback': 0.3, 'mix': 0.2}),
    ('limiter', {'ceiling_db': -1.0, 'input_gain_db': 0}),
    ('hum_remove', {'frequency': 60, 'harmonics': 4, 'strength': 0.7}),
    ('de_ess', {'frequency': 6000, 'reduction_db': 6}),
    ('normalize', {'target_db': -1.0, 'mode': 'peak'}),
    ('crossfade', {'duration_ms': 200, 'curve': 'equal_power'}),
    ('time_stretch', {'rate': 0.8}),
    ('pitch_shift', {'semitones': -3, 'cents': 25}),
    ('stereo_width', {'width': 50}),
    ('de_clip', {'sensitivity': 70}),
    ('reverse', {}),
]

for fx_name, params in effects:
    d2 = requests.post(f'{BASE}/api/track/add',
        json={'file_path': TEST_FILE, 'name': f'FX_{fx_name}'}, timeout=10).json()
    ftid = d2.get('track_id', tid)
    d = test(f'FX: {fx_name}', 'POST', '/api/fx/apply',
        {'track_id': ftid, 'effect': fx_name, 'params': params})
    # Verify output file
    if d.get('ok') and d.get('output'):
        exists = os.path.exists(d['output'])
        if not exists:
            results.append((f'FX file: {fx_name}', 'FAIL', 200, 'missing'))
            print(f'  [X] FX output missing: {fx_name}')

# 8. MEASUREMENT
print('\n--- [8] MEASUREMENT & ANALYSIS ---')
d = test('LUFS', 'POST', '/api/fx/measure', {'track_id': tid})
print(f'       LUFS: {d.get("lufs")}, Peak: {d.get("true_peak")}')
d = test('Analyze', 'POST', '/api/analyze', {'file_path': TEST_FILE})
print(f'       Key: {d.get("key")}, BPM: {d.get("bpm")}')

# 9. EDITING
print('\n--- [9] EDITING ---')
test('Detect channels', 'POST', '/api/edit/detect-channels', {'file_path': TEST_FILE})
test('Detect silence', 'POST', '/api/edit/detect-silence', {'path': TEST_FILE})
test('Count-in', 'POST', '/api/edit/count-in', {'bpm': 120, 'bars': 2})
test('Split', 'POST', '/api/edit/split', {'track_id': tid})

# 10. MONITORING
print('\n--- [10] INPUT MONITORING ---')
test('Monitor on', 'POST', '/api/monitor/toggle')
test('Monitor off', 'POST', '/api/monitor/toggle')

# 11. AI
print('\n--- [11] AI FEATURES ---')
d = test('Bandmate', 'POST', '/api/bandmate',
    {'message': 'What key pairs with E minor?', 'context': {'key': 'Em', 'bpm': '140'}})
resp = d.get('response', '')
print(f'       Response: {resp[:60]}...' if len(resp) > 60 else f'       Response: {resp}')

# 12. EXPORT
print('\n--- [12] EXPORT ---')
d = test('Export WAV', 'POST', '/api/export', {'format': 'wav', 'sample_rate': 44100})
if d.get('path'):
    exists = os.path.exists(d['path'])
    results.append(('WAV file exists', 'PASS' if exists else 'FAIL', 200, ''))
    print(f'       File: {d["path"]} ({"exists" if exists else "MISSING"})')

d = test('Export FLAC', 'POST', '/api/export', {'format': 'flac', 'sample_rate': 48000})
if d.get('path'):
    exists = os.path.exists(d['path'])
    results.append(('FLAC file exists', 'PASS' if exists else 'FAIL', 200, ''))

# 13. PROJECT
print('\n--- [13] PROJECT ---')
test('Save', 'POST', '/api/project/save',
    {'version': '0.1.0', 'tracks': [{'id': 0, 'name': 'Test'}], 'savedAt': '2026-04-17'})
d = test('Recover', 'GET', '/api/project/recover')
avail = d.get('available', False)
results.append(('Recovery available', 'PASS' if avail else 'FAIL', 200, ''))

# ═══ SUMMARY ═══
print('\n' + '=' * 70)
passes = sum(1 for _, s, _, _ in results if s == 'PASS')
fails = sum(1 for _, s, _, _ in results if s == 'FAIL')
errors = sum(1 for _, s, _, _ in results if s == 'ERROR')
total = len(results)
print(f'  RESULTS: {passes}/{total} PASS | {fails} FAIL | {errors} ERROR')
print('=' * 70)

if fails or errors:
    print('\n  FAILURES:')
    for name, status, code, err in results:
        if status != 'PASS':
            print(f'    [{status}] {name} [{code}] {err}')
else:
    print('  >>> ALL TESTS PASS -- CLEAN <<<')

# Return exit code
sys.exit(1 if (fails or errors) else 0)
