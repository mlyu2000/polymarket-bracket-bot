import json

prev = {}
with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
supp = json.load(open('_tmp_cron_20261010T081459Z_supp_data.json'))
cur_band = supp['band']
prev_band = last['near_1.000_1.005']
prev_names = {r[1] for r in prev_band}
cur_names = {r[1] for r in cur_band}
prev_lookup = {r[1]: r for r in prev_band}
entry = {
    'ts_utc': '2026-10-10T08:20Z',
    'markets': supp['markets'],
    'scan_time_s': 49.0,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in cur_band],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
        "min-ask floor authoritative. FLOOR BROKE 1.005->1.004 — first improvement after "
        "six consecutive runs at 1.005; band n=3->3 same members; "
        f"Kyōto improved Yes@{prev_lookup['Kyōto Sanga FC vs. FC Machida Zelvia: O/U 7.5'][2]}->{cur_band[0][2]} sum 1.005->1.004 liq 8799.97->8659.27 (-1.6%); "
        "Clermont unchanged 0.008/0.997 liq 2571.81->2787.53 (+8.4%); "
        "South Melbourne Yes 0.014->0.015 sum held 1.005 liq 9766.74->9462.10 (-3.1%). "
        "NOTE: mid-run supp_minask pull (~08:16Z) still showed floor 1.005 (Kyōto Yes@0.010) — "
        "book moved 0.001 lower within ~2 min; final pull authoritative. "
        "Next tier (1.005,1.01]: Chornomorets DROPPED OUT of next tier (was 1.006 liq 4683.6); "
        "Kolos/Epitsentr 1.006 liq 2657.5->2470.78 -7.0%, Falkirk 1.006 3528.6->3488.41 -1.1%, "
        "Al Ettifaq/Al Khaleej 1.008 5063.8->3138.18 -38.0%, Hajduk/Dinamo 1.008 4522.4->4336.65 -4.1%; "
        "1.01 tier crowded (AEK, Asteras, Vasco, RAAL, Rayo, Zulte, Sheffield BTTS, Harrogate, Iran, Stjarnan, Rizespor). "
        f"adds {sorted(cur_names - prev_names)}, drops {sorted(prev_names - cur_names)}. "
        "priced 69->67. Detector opportunities: 0. Paper trades: 0. "
        "No sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
        "floor 1.004, best gross edge -0.004 vs parity; still 0.024 above the 0.98 actionable threshold "
        "(sum <= 1 - fee 0.005 - slip 0.005 - margin 0.01)."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry, ensure_ascii=False)[:300], '...')
