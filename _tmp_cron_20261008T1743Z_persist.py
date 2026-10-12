import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1743Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

entry = {
    "ts_utc": ts,
    "markets": 500,
    "scan_time_s": 48.6,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. Floor held at 1.002 but MEMBERSHIP ROTATED: 1728Z holder 'Will Apple largest company' (.120/.882 liq 169610) dropped out of active 500-set entirely (verified by direct re-check, not a price move); Dortmund 0-3 Werder improved 1.003->1.002 (yes .005/no .997, liq 26040) now sole floor holder. West Ham held 1.003. Band 9->8. NEW band member: Dortmund 2-4 Werder 1.005. Held: CA Paranaense O/U7.5, Sochaux 3-3 Boulogne, Montpellier 0-3 Grenoble, Kashiwa O/U7.5, US-unemployment 6.0%. Priced 108->110 (+2). No sub-1.00. Paper trades 0."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
