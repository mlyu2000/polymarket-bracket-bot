import json, subprocess
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1635Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = near[0][0] if near else None
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'
run = now.strftime('%Y%m%dT%H%M%SZ')

# Append to results/cron_scan_history.jsonl (schema of prior entries)
entry = {
    "ts_utc": ts,
    "markets": 500,
    "scan_time_s": 49.7,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. Floor FELL 1.005->1.003 (West Ham no .997->.995); band narrowed 4->3 (Palmeiras left band)."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')

msg = (f"runs: {run} scan+persist "
       f"(500 markets, 0 brackets; verbatim asks0 scan 55.2s: 0 BRACKETS, 0 asks0 near-misses (known DESC artifact); "
       f"supp minask 49.7s: floor FELL back 1.005->1.003 - West Ham 0-3 QPR re-entered sub-1.005 (no .997->.995, liq 10699); "
       f"band<=1.005 narrowed 4->3 (Palmeiras left band at >=1.006; CA Paranaense 1.005 liq 5138, Kashiwa 1.005 liq 3499 held); "
       f"priced 111->{d['priced']} (+1); detector-opps: {len(opps)}, paper: no executions)")

open(f'_tmp_cron_{run}_runlog.txt', 'w').write(msg)
subprocess.run(['git', 'add', '_tmp_cron_20261008T1635Z_scan_out.txt',
                '_tmp_cron_20261008T1635Z_supp_out.txt',
                '_tmp_cron_20261008T1635Z_supp_data.json',
                'results/cron_scan_history.jsonl'], check=True)
subprocess.run(['git', 'commit', '-m', msg], check=True)
subprocess.run(['git', 'push'], check=False)
print('committed:', run)
