import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1813Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

entry = {
    "ts_utc": ts,
    "markets": 500,
    "scan_time_s": 50.0,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR IMPROVED 1.003->1.002: Dortmund 0-3 Werder yes .006->.005 (liq 31203) is sole floor holder again (as at 1743Z). West Ham held 1.003; US-unemployment improved 1.005->1.004. Band membership UNCHANGED at 8 vs 1758Z (Dortmund 0-3, West Ham, US-unemp, CA Paranaense O/U7.5, Dortmund 2-4, Sochaux 3-3, Montpellier 0-3, Kashiwa O/U7.5). Priced 109->105 (-4 settling). No sub-1.00. Paper trades 0."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))