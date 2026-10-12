import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1843Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

prev = [json.loads(l) for l in open('results/cron_scan_history.jsonl')]
prev_band = {q for _, q, *_ in prev[-1]['near_1.000_1.005']}
cur_band = {q for _, q, *_ in near}
added = sorted(cur_band - prev_band)
dropped = sorted(prev_band - cur_band)

entry = {
    "ts_utc": ts,
    "markets": 500,
    "scan_time_s": 48.8,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             f"Floor regressed 1.002->1.003: Dortmund 0-3 Werder yes .005->.006 (liq 30757) ties with West Ham 1.003 as joint floor holders. "
             f"Band 8->7 MEMBERSHIP CHANGED; priced 106->104. Added: {added}. Dropped: {dropped}. "
             "Drop causes verified by direct re-check: Sochaux 3-3 Boulogne moved 1.005->1.006 (yes .010->.011); "
             "Cluj O/U7.5 collapsed 1.004->1.359 (yes .005->.36, liq 2105->22 — market effectively dying). "
             "US-unemployment held 1.004. No sub-1.00. Paper trades 0.")
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
print('added:', added)
print('dropped:', dropped)
