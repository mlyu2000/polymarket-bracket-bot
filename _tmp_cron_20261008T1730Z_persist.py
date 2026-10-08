import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1730Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

entry = {
    "ts_utc": ts,
    "markets": 500,
    "scan_time_s": 51.8,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. Floor steady at 1.003 (West Ham 0-3 QPR). Band 4 members (all >=1.003). No sub-1.00 brackets."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
