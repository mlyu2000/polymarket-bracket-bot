import json

prev = json.loads(open('_tmp_cron_20261010T100418Z_prev.json').read().strip())

# this run's data (verbatim scan + supp min-ask)
scan_markets = 500
scan_time = 48.4
priced = 69
floor = 1.005
band = [[1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.008, 0.997, 2938.71408]]
# detail pass (0.3s later snapshot) for next-tier context
top20_next = [
    (1.006, "Falkirk FC vs. Dundee FC: O/U 7.5", 3714.64301),
    (1.008, "Al Ettifaq Saudi Club vs. Al Khaleej Saudi Club: O", 3232.85424),
    (1.008, "HNK Hajduk Split vs. GNK Dinamo Zagreb: O/U 7.5", 2889.54059),
    (1.010, "Asteras Tripolis vs. Atromitos Athinon: O/U 1.5", 10174.4003),
    (1.010, "Atalanta BC vs. Venezia FC: O/U 2.5", 47509.1056),
]

pmap = {r[1][:20]: r for r in prev['near_1.000_1.005']}

note_parts = []
note_parts.append("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative.")
note_parts.append("FLOOR REVERTED 1.002->1.005 after 3 consecutive break-runs (1.004->1.003->1.002); band n=3->1, only Clermont survives.")
for r in band:
    key = r[1][:20]
    p = pmap.get(key)
    if p:
        dl = (r[4]-p[4])/p[4]*100
        note_parts.append("%s sum %.3f->%.3f Yes@%.3f->%.3f No@%.3f->%.3f liq %.2f->%.2f (%+.1f%%)" % (r[1][:14], p[0], r[0], p[2], r[2], p[3], r[3], p[4], r[4], dl))
    else:
        note_parts.append("%s ENTERS band %.3f Yes@%.3f No@%.3f liq %.2f" % (r[1][:14], r[0], r[2], r[3], r[4]))
for r in prev['near_1.000_1.005']:
    key = r[1][:20]
    if key not in {b[1][:20] for b in band}:
        note_parts.append("%s DROPPED OUT of band (was %.3f Yes@%.3f No@%.3f liq %.2f; now outside top-20 min-ask sums => unpriced or >1.020)" % (r[1][:14], r[0], r[2], r[3], r[4]))
note_parts.append("priced %d->%d (books thinning between snapshots)" % (prev['priced_minask'], priced))
note_parts.append("next tier: " + "; ".join("%.3f liq %.1f %s" % (t, l, q[:18]) for t, q, l in top20_next))
note_parts.append("detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge, no actionable arb; floor 1.005, best gross edge -0.005, still 0.025 above 0.98 actionable threshold")

rec = {
    "ts_utc": "2026-10-10T10:04Z",
    "markets": scan_markets,
    "scan_time_s": round(scan_time, 1),
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": priced,
    "best_ask_floor": floor,
    "near_1.000_1.005": band,
    "detector_opps": 0,
    "paper_trades": 0,
    "note": " ".join(note_parts),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("appended:", json.dumps(rec, ensure_ascii=False)[:500])
