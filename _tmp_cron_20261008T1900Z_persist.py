import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1900Z_supp_data.json'))
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
    "scan_time_s": 51.0,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             f"Floor improved 1.003->1.002: Dortmund 0-3 Werder yes .006->.005 (liq 30757->44342) sole holder again. "
             f"Band UNCHANGED at 7 members (added {added}, dropped {dropped}). "
             "US-unemployment degraded 1.004->1.005 (no .996->.997); West Ham held 1.003; 1.005 tier steady "
             "(Paranaense/Mineiro, Dortmund 2-4, Montpellier, Kashiwa). Priced 104->103. No sub-1.00. Paper trades 0.")
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
print('added:', added)
print('dropped:', dropped)
