import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T1920Z_supp_data.json'))
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
    "scan_time_s": d['scan_time'],
    "brackets_verbatim": len(opps),
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             f"Floor HELD at 1.001 (US unemployment yes=.004 No=.997, liq 7997->7813); Dortmund 0-3 held 1.002; West Ham held 1.003; "
             f"Paranaense/Mineiro 1.004 (liq 14592->15324). Band UNCHANGED at 7 members (added {added}, dropped {dropped}). Priced 101 stable. "
             "1.001 > 1.000 — no actionable bracket. Paper trades 0.")
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
print('added:', added)
print('dropped:', dropped)
