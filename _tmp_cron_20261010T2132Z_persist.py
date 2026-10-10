import json
supp = json.load(open('_tmp_cron_20261010T2132Z_supp_data.json'))
prev = None
for l in open('results/cron_scan_history.jsonl').read().strip().split('\n'):
    if not l.strip():
        continue
    try:
        d = json.loads(l)
    except json.JSONDecodeError:
        continue
    if d.get('ts_utc') == '2026-10-10T2132Z':
        prev = d
entry = {
    'ts_utc': '2026-10-10T2132Z',
    'markets': supp['markets'],
    'scan_time_s': 76.0,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
             "min-ask floor authoritative. TRUE FLOOR 1.0050 — 3-way tie (Calcio Padova vs. "
             "Carrarese O/U 7.5 Yes@0.010 No@0.995 liq 3040.36; Gaziantep FK vs. Çorum FK O/U 7.5 "
             "liq 4103.44; JEF United vs. V-Varen Nagasaki O/U 7.5 liq 4296.63). vs 20:40Z run: "
             "band shrank n=4->3 — CA River Plate/AA Estudiantes O/U 7.5 climbed out of band "
             "(liq had deepened 2783->6146), and Al Fayha/Al Riyadh dropped 1.005->1.006 as its "
             "YES ask moved 0.009->0.010. Next tier 1.006 (Al Fayha, LNZ Cherkasy, Konyaspor, "
             "Silkeborg), 1.007 Dynamo Kyiv/Karpaty. Book health: 65/500 both-sided, 412 one-sided, "
             "21 both-empty — one-sided dominance entrenched (+4 vs 20:40Z's 408); API healthy, "
             "no fetch failures. Floor 1.005 still 0.025 above 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended entry for', entry['ts_utc'], '| floor', entry['best_ask_floor'], '| prev same-label floor', prev['best_ask_floor'] if prev else 'n/a')
