import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T2210Z_supp_data.json'))
near = d['near']
opps = d['opps']
floor = d['true_floor']
now = datetime.now(timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M') + 'Z'

prev = [json.loads(l) for l in open('results/cron_scan_history.jsonl')]
last = prev[-1]
prev_band = {q for _, q, *_ in last['near_1.000_1.005']}
cur_band = {q for _, q, *_ in near}
added = sorted(cur_band - prev_band)
dropped = sorted(prev_band - cur_band)

note = ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        f"FLOOR RISEN {last['best_ask_floor']}->{floor}: sole holder 'US unemployment 6.0%' dropped out of <=1.005 band "
        "(all-time min 1.001 no longer standing). New floor holder: CA Paranaense vs. CA Mineiro O/U 7.5, improved 1.005->1.002. "
        f"Band {len(prev_band)}->{len(cur_band)}: added {added if added else 'none'}, dropped {dropped if dropped else 'none'}. "
        f"Priced {last['priced_minask']}->{d['priced']}. "
        "Movers: Nordsjaelland/Odense O-U 8.5 slipped 1.002->1.003, Dortmund 0-3 held 1.003, West Ham 0-3 held 1.004, 1.005 tier x3 held. "
        "Detector (true min-ask, sum<1.00): 0 brackets — no actionable arb. Paper trades 0.")

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
    "note": note,
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + "\n")
print("appended:", ts, "floor:", floor, "priced:", d['priced'])
