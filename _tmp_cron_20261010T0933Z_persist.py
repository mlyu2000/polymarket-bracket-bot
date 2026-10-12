import json

scan = json.load(open('_tmp_cron_20261010T0933Z_scan_data.json'))
supp = json.load(open('_tmp_cron_20261010T0933Z_supp_data.json'))

band = supp['band']
priced = supp['priced']

prev = json.loads(open('results/cron_scan_history.jsonl').read().strip().splitlines()[-1])
pmap = {r[1][:20]: r for r in prev['near_1.000_1.005']}

note_parts = []
note_parts.append("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative.")
note_parts.append("FLOOR BROKE 1.003->1.002 (3rd break in 4 runs): Kyoto No 0.996->0.995 Yes held 0.007; band n=2->3 Kolos/Epitsentr RE-ENTERS at 1.004.")
for r in band:
    key = r[1][:20]
    p = pmap.get(key)
    if p:
        dl = (r[4]-p[4])/p[4]*100
        note_parts.append("%s sum %.3f->%.3f Yes@%.3f->%.3f No@%.3f->%.3f liq %.2f->%.2f (%+.1f%%)" % (r[1][:14], p[0], r[0], p[2], r[2], p[3], r[3], p[4], r[4], dl))
    else:
        note_parts.append("%s ENTERS band %.3f Yes@%.3f No@%.3f liq %.2f" % (r[1][:14], r[0], r[2], r[3], r[4]))
note_parts.append("priced %d->%d" % (prev['priced_minask'], priced))
nt = [r for r in supp['top20'][len(band):len(band)+5]]
note_parts.append("next tier: " + "; ".join("%.3f liq %.1f %s" % (r[0], r[4], r[1][:18]) for r in nt))
note_parts.append("detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge, no actionable arb; floor 1.002, best gross edge -0.002, still 0.022 above 0.98 actionable threshold")

rec = {
    "ts_utc": "2026-10-10T09:33Z",
    "markets": scan['markets'],
    "scan_time_s": round(scan['scan_time'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": len(scan['near_misses']),
    "priced_minask": priced,
    "best_ask_floor": supp['floor'],
    "near_1.000_1.005": band,
    "detector_opps": len(scan['opps']),
    "paper_trades": len(scan['opps']),
    "note": " ".join(note_parts),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("appended:", json.dumps(rec, ensure_ascii=False)[:400])
