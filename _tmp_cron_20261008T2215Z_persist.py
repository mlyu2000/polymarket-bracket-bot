import json
from datetime import datetime, timezone

d = json.load(open('_tmp_cron_20261008T2215Z_supp_data.json'))
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
        f"FLOOR DROPPED {last['best_ask_floor']}->{floor}: new floor holder 'lowest temperature in Milan 17°C or higher' (1.001) "
        "entered band but liq=11.9 < MIN_LIQUIDITY_USDC=100 — filtered by detector, not tradable. "
        "Best liquid floor remains CA Paranaense vs. CA Mineiro O/U 7.5 at 1.002. "
        f"Band {len(prev_band)}->{len(cur_band)}: added {added if added else 'none'}, dropped {dropped if dropped else 'none'}. "
        f"Priced {last['priced_minask']}->{d['priced']}. "
        "Movers: Dortmund 0-3 improved 1.003->1.002; Paranaense held 1.002, Nordsjaelland/Odense held 1.003, West Ham 0-3 held 1.004, 1.005 tier x3 held. "
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
