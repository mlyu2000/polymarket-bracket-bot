import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1618Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

entry = {
    "ts_utc": ts,
    "markets": d['markets'],
    "scan_time_s": round(d['scan_time'], 1),
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR BROKE 1.003->1.002: Union Touarga 2-0 RS Berkane (yes .020/no .982) but liq only $502 -> below MIN_LIQUIDITY, no trade. Band 8->10. NEW: Ipswich 3-4 Fulham 1.003 (liq 15252), Ipswich 4-3 Fulham 1.004, Ipswich 2-5 Fulham 1.005. Dortmund 1.003 + West Ham 1.003 held. Hoffenheim 0-3 HSV LEFT band. No sub-1.00. Paper trades 0."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
