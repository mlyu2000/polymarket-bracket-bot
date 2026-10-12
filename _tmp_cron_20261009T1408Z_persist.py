import json

TS = "2026-10-09T14:08Z"
scan = json.load(open('_tmp_cron_20261009T1408Z_scan_data.json'))
supp = json.load(open('_tmp_cron_20261009T1408Z_supp_data.json'))

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])
prev_band = [tuple(x) for x in prev['near_1.000_1.005']]

band = [r for r in supp['band'] if 1.0 <= r['sum'] <= 1.005]
# dedupe identical (sum, question) rows (duplicate market listings)
seen = set()
band_u = []
for r in band:
    key = (round(r['sum'], 3), r['q'])
    if key not in seen:
        seen.add(key)
        band_u.append(r)
near = [[round(r['sum'], 3), r['q'], r['yes'], r['no'], r['liq']] for r in band_u]
cur_set = {(round(r['sum'], 3), r['q']) for r in band_u}
prev_set = {(round(t[0], 3), t[1]) for t in prev_band}
adds = sorted(cur_set - prev_set, key=lambda x: x[0])
drops = sorted(prev_set - cur_set, key=lambda x: x[0])
# intra-band price shifts for entries present in both
cur_map = {(round(r['sum'], 3), r['q']): (r['yes'], r['no']) for r in band_u}
prev_map = {(round(t[0], 3), t[1]): (t[2], t[3]) for t in prev_band}
shifts = [(q, prev_map[k], cur_map[k]) for k in (cur_set & prev_set) for _, q in [k] if prev_map[k] != cur_map[k]]
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
    "Band " + str(len(prev_band)) + "->" + str(len(band_u)) + " (dup Clermont row deduped): adds " + (str(fmt(adds)) if adds else "none")
    + ", drops " + (str(fmt(drops)) if drops else "none") + ". "
    "Intra-band shifts: " + (str([(q, p, c) for q, p, c in shifts]) if shifts else "none (survivors unchanged)") + ". "
    "Priced " + str(prev['priced_minask']) + "->" + str(supp['priced']) + ". "
    "Detector opportunities: " + str(supp['detector_opps']) + ". "
    "True brackets (min-ask sum<1.00): " + str(len(brackets)) + " — no actionable arb. "
    "Paper trades " + str(len(scan['opps'])) + "."
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

msg = ("runs: " + TS + " scan+persist (500 markets, 0 brackets; verbatim asks0 scan "
       + str(round(scan['scan_time'], 1)) + "s: 0 BRACKETS, 0 asks0 near-misses (known DESC artifact); supp minask "
       + str(round(supp['elapsed'], 1)) + "s: " + str(supp['priced']) + "/500 priced, floor "
       + str(prev_floor) + "->" + str(floor) + " " + trend + " (WestHam 0-3 QPR Yes@0.007+No@0.995); band "
       + str(len(prev_band)) + "->" + str(len(band_u)) + ": adds " + (str(fmt(adds)) if adds else "none")
       + ", drops " + (str(fmt(drops)) if drops else "none")
       + "; intra-band shifts: " + ("none (survivors prices identical)" if not shifts else str(shifts))
       + "; priced 95->" + str(supp['priced']) + "; detector-opps: " + str(supp['detector_opps'])
       + ", paper: no executions)")
open('_tmp_cron_20261009T1408Z_commitmsg.txt', 'w').write(msg)
print("appended:", json.dumps(rec, indent=2))
print("MSG:", msg)
