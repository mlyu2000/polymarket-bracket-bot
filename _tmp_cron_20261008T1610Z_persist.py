import json, subprocess, time
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1610Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = near[0][0] if near else None

msg = (f"runs: {datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')} scan+persist "
       f"(500 markets, 0 brackets; verbatim asks0 scan 49.8s: 0 BRACKETS, 0 asks0 near-misses (known DESC artifact); "
       f"supp minask 50.2s: floor 1.003 West Ham 0-3 QPR yes .008/no .995 liq 10526 (1.002->1.003 widened); "
       f"band<=1.005 narrowed 5->4 (US-unemployment and Warsaw left band; CA Paranaense 1.005, Kashiwa 1.005, Palmeiras 1.005 held); "
       f"priced 109->{d['priced']}; detector-opps: {len(opps)}, paper: no executions)")

open('_tmp_cron_20261008T1610Z_runlog.txt', 'w').write(msg)
subprocess.run(['git', 'add', '_tmp_cron_20261008T1610Z_scan_out.txt',
                '_tmp_cron_20261008T1610Z_supp_out.txt', '_tmp_cron_20261008T1610Z_supp_data.json'],
               check=True)
subprocess.run(['git', 'commit', '-m', msg], check=True)
subprocess.run(['git', 'push'], check=False)
print('committed')
