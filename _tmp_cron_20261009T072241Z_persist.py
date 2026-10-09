import json

TS = "2026-10-09T07:22Z"

# Verbatim scan results (stdout): 500 markets in 48.2s, 0 brackets, 0 asks0 near-misses
scan = {'scan_time': 48.2, 'markets': 500, 'opps': [], 'near_misses': []}

# Supplementary min-ask run (_tmp_cron_20261009T072241Z_supp_minask.py) output rows:
supp = {
    'markets': 500,
    'priced': 85,
    'rows': [
        {'sum': 1.002, 'yes': 0.005, 'no': 0.997, 'q': 'Exact Score: BV Borussia 09 Dortmund 0 - 3 SV Werder Bremen?', 'liq': 65179.55669},
        {'sum': 1.004, 'yes': 0.008, 'no': 0.996, 'q': 'Exact Score: Montpellier HSC 0 - 3 Grenoble Foot 38?', 'liq': 8290.7841},
        {'sum': 1.004, 'yes': 0.008, 'no': 0.996, 'q': 'Exact Score: West Ham United FC 0 - 3 Queens Park Rangers FC', 'liq': 29334.30827},
        {'sum': 1.005, 'yes': 0.015, 'no': 0.990, 'q': 'FC Nordsjælland vs. Odense BK: O/U 8.5', 'liq': 7465.27157},
        {'sum': 1.005, 'yes': 0.010, 'no': 0.995, 'q': 'Kashiwa Reysol vs. Vissel Kōbe: O/U 7.5', 'liq': 32311.14305},
        {'sum': 1.006, 'yes': 0.011, 'no': 0.995, 'q': "Exact Score: FC Sochaux-Montbéliard 3 - 3 US Boulogne Côte d'Opale?", 'liq': 11243.39137},
        {'sum': 1.006, 'yes': 0.010, 'no': 0.996, 'q': 'Exact Score: Montpellier HSC 3 - 3 Grenoble Foot 38?', 'liq': 9312.98096},
        {'sum': 1.008, 'yes': 0.014, 'no': 0.994, 'q': "FC Sochaux-Montbéliard vs. US Boulogne Côte d'Opale: O/U 6.5", 'liq': 4329.94481},
    ],
}
with open('_tmp_cron_20261009T072241Z_supp_data.json', 'w') as f:
    json.dump(supp, f)

rows = supp['rows']
floor = rows[0]['sum'] if rows else None
near = [[r['sum'], r['q'][:50], r['yes'], r['no'], r['liq']] for r in rows if 1.0 <= r['sum'] <= 1.005]
brackets = [r for r in rows if r['sum'] < 1.0]

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
prev = json.loads(lines[-1])
prev_band = sorted({q for _, q, *_ in prev.get('near_1.000_1.005', [])})
cur_band = sorted({q for _, q, *_ in near})
adds = [q for q in cur_band if q not in prev_band]
drops = [q for q in prev_band if q not in cur_band]

note = (
    "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
    f"min-ask floor authoritative. FLOOR {prev['best_ask_floor']}->{floor} "
    f"{'fell back' if float(floor) < float(prev['best_ask_floor']) else ('rose' if float(floor) > float(prev['best_ask_floor']) else 'held')}. "
    f"Band {len(prev_band)}->{len(near)}: adds {adds if adds else 'none'}, drops {drops if drops else 'none'}. "
    f"Priced {prev['priced_minask']}->{supp['priced']}. "
    f"Detector (true min-ask, sum<1.00): {len(brackets)} brackets — no actionable arb. "
    f"Paper trades {len(scan['opps'])}."
)

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(scan['scan_time'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": len(scan['near_misses']),
    "priced_minask": supp['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": note,
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")

with open('results/scan_latest.json', 'w') as f:
    json.dump(rec, f, indent=2)

print("appended:", json.dumps(rec, indent=2)[:2500])
