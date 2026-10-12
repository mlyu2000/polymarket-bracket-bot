import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1728Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

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
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR IMPROVED 1.003->1.002: new member 'Will Apple be the largest company in the world' Yes .120/No .882 liq 169,610 - first high-liquidity market at the floor (prior floor members were all settled-ish exact-score markets). Band widened 8->9 (Sochaux 3-3 Boulogne 1.005 NEW; Union Touarga 2-0 Berkane left band). Dortmund + West Ham held at 1.003. Priced steady 108/500. No sub-1.00 brackets. Paper trades 0."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
