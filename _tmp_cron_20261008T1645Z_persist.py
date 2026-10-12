import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1645Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

entry = {
    "ts_utc": ts,
    "markets": 500,
    "scan_time_s": 48.0,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. Floor back 1.002->1.003 (Union Touarga low-liq 1.002 entry left band). Floor band 1.003 now 2 members: Dortmund 0-3 Werder (yes .006/no .997, liq 33646), West Ham 0-3 QPR (yes .008/no .995, liq 24262). Band narrowed 10->6: Ipswich-Fulham trio (3-4, 4-3, 2-5) + Union Touarga all LEFT; held: CA Paranaense, Montpellier 0-3 Grenoble, Kashiwa, US-unemployment at 1.005. Priced 113->108. No sub-1.00. Paper trades 0."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
