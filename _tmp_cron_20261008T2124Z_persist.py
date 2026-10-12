import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T2124Z_supp_data.json'))
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
    "markets": d['markets'],
    "scan_time_s": round(d['scan_time'], 1),
    "brackets_verbatim": len(opps),
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             f"FLOOR HELD at 1.001 (all-time min): US-unemployment yes .004 sole holder (liq 7775->{near[0][4]:.0f}); "
             f"Dortmund 0-3 Werder held 1.002; West Ham 0-3 + Nordsjaelland/Odense O-U 8.5 held 1.003; "
             f"1.005 tier x6. Band {len(prev_band)}->{len(cur_band)}: added {added if added else 'none'}, dropped {dropped if dropped else 'none'}. "
             f"Priced {prev[-1]['priced_minask']}->{d['priced']}. "
             "1.001 still > 1.000 detector threshold — no actionable bracket. Paper trades 0.")
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted', ts, 'floor', floor, 'band', len(near), 'brackets', len(opps))
print('added:', added)
print('dropped:', dropped)
