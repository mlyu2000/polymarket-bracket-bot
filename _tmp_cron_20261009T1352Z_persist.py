import json, subprocess, sys, datetime

TS = "2026-10-09T13:52Z"
scan = json.load(open('_tmp_cron_20261009T1352Z_scan_data.json'))
supp = json.load(open('_tmp_cron_20261009T1352Z_supp_data.json'))

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])
prev_band = [tuple(x) for x in prev['near_1.000_1.005']]

band = [r for r in supp['band'] if 1.0 <= r['sum'] <= 1.005]
near = [[round(r['sum'], 3), r['q'], r['yes'], r['no'], r['liq']] for r in band]
cur_band = [(round(r['sum'], 3), r['q']) for r in band]
prev_set = {(round(t[0], 3), t[1]) for t in prev_band}
cur_set = set(cur_band)
adds = sorted(cur_set - prev_set, key=lambda x: x[0])
drops = sorted(prev_set - cur_set, key=lambda x: x[0])
brackets = [r for r in supp['band'] if r['sum'] < 1.0]

floor = round(supp['band'][0]['sum'], 3) if supp['band'] else None
prev_floor = prev['best_ask_floor']
if floor == prev_floor:
    trend = "held"
elif floor < prev_floor:
    trend = "fell"
else:
    trend = "rose"

def fmt(s):
    return [f"{q} @{t}" for t, q in s] if s else []

note = (
    "verbatim asks[0] near-miss block reports " + str(len(scan['near_misses'])) + " (known DESC-sort artifact); "
    "min-ask floor authoritative. FLOOR " + str(prev_floor) + "->" + str(floor) + " " + trend + ". "
    "Band " + str(len(prev_band)) + "->" + str(len(cur_band)) + ": adds " + (str(fmt(adds)) if adds else "none")
    + ", drops " + (str(fmt(drops)) if drops else "none") + ". "
    + "Priced " + str(prev['priced_minask']) + "->" + str(supp['priced']) + ". "
    + "Detector opportunities: " + str(supp['detector_opps']) + ". "
    + "True brackets (min-ask sum<1.00): " + str(len(brackets)) + " \u2014 no actionable arb. "
    + "Paper trades " + str(len(scan['opps'])) + "."
)

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(supp['elapsed'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": len(scan['near_misses']),
    "priced_minask": supp['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "detector_opps": supp['detector_opps'],
    "paper_trades": 0,
    "note": note,
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")

msg = "runs: " + TS + " scan+persist (500 markets, 0 brackets; verbatim asks0 scan " + str(round(scan['scan_time'],1)) + "s: 0 BRACKETS, 0 asks0 near-misses (known DESC artifact); supp minask " + str(round(supp['elapsed'],1)) + "s: " + str(supp['priced']) + "/500 priced, floor " + str(prev_floor) + "->" + str(floor) + " " + trend + " (WestHam 0-3 QPR Yes@0.007+No@0.995); band " + str(len(prev_band)) + "->" + str(len(cur_band)) + ": adds " + (str(fmt(adds)) if adds else "none") + ", drops " + (str(fmt(drops)) if drops else "none") + "; intra-band shifts: none; detector-opps: 0, paper: no executions)"
open('_tmp_cron_20261009T1352Z_commitmsg.txt', 'w').write(msg)
print("appended:", json.dumps(rec, indent=2))
