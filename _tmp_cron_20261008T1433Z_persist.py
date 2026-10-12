import json, subprocess
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1433Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = near[0][0] if near else None
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'
run = now.strftime('%Y%m%dT%H%M%SZ')

entry = {
    "ts_utc": ts,
    "markets": 500,
    "scan_time_s": round(d['scan_time'], 1),
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. Floor HELD 1.003 (West Ham 0-3 QPR); band widened 3->4 (US-unemployment re-entered at 1.005); priced 112->110 (-2)."
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')

msg = (f"runs: {run} scan+persist "
       f"(500 markets, 0 brackets; verbatim asks0 scan 50.7s: 0 BRACKETS, 0 asks0 near-misses (known DESC artifact); "
       f"supp minask {d['scan_time']:.1f}s: floor HELD 1.003 - West Ham 0-3 QPR yes .008/no .995 liq 10700; "
       f"band<=1.005 widened 3->4 (US-unemployment re-entered at 1.005 yes .009/no .996 liq 3184; CA Paranaense 1.005 liq 5176, Kashiwa 1.005 liq 3523 held); "
       f"priced 112->{d['priced']} (-2); detector-opps: {len(opps)}, paper: no executions)")

open(f'_tmp_cron_{run}_runlog.txt', 'w').write(msg)
subprocess.run(['git', 'add', '_tmp_cron_20261008T1433Z_scan_out.txt',
                '_tmp_cron_20261008T1433Z_supp_out.txt',
                '_tmp_cron_20261008T1433Z_supp_data.json',
                'results/cron_scan_history.jsonl'], check=True)
subprocess.run(['git', 'commit', '-m', msg], check=True)
subprocess.run(['git', 'push'], check=False)
print('committed:', run)
