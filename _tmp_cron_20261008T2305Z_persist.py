import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T2305Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

prev = [json.loads(l) for l in open('results/cron_scan_history.jsonl')]
last = prev[-1]
prev_band = {q for _, q, *_ in last['near_1.000_1.005']}
cur_band = {q for _, q, *_ in near}
added = sorted(cur_band - prev_band)
dropped = sorted(prev_band - cur_band)
prev_totals = {q: t for t, q, *_ in last['near_1.000_1.005']}
movers = [f"{q}: {prev_totals[q]:.3f}->{t:.3f}" for t, q, *_ in near if q in prev_totals and abs(prev_totals[q]-t) > 1e-9]

note = ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        f"FLOOR {last['best_ask_floor']}->{floor} held by Dortmund 0-3 (Paranaense O/U 7.5 co-hold gone; O/U 5.x now 1.004). "
        f"Band {len(prev_band)}->{len(cur_band)}: added {added if added else 'none'}, dropped {dropped if dropped else 'none'}. "
        f"Priced {last['priced_minask']}->{d['priced']}. "
        f"Movers: {movers if movers else 'none'}. "
        "Detector (true min-ask, sum<1.00): 0 brackets — no actionable arb. Paper trades 0.")

entry = {
    "ts_utc": ts,
    "markets": d['markets'],
    "scan_time_s": round(d['scan_time'], 1),
    "brackets_verbatim": len(opps),
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": note,
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, default=str) + '\n')
print("persisted:", ts, "| floor", floor, "| band", len(cur_band), "| priced", d['priced'])
