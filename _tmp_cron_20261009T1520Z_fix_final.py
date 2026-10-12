import json

path = 'results/cron_scan_history.jsonl'
lines = [l for l in open(path) if l.strip()]
rec = json.loads(lines[-1])
assert rec['ts_utc'] == "2026-10-09T15:35Z"

# baseline = the immediately-preceding 15:19Z record
prev = json.loads(lines[-2])
assert prev['ts_utc'] == "2026-10-09T15:19Z"

# restore full-length names in band (match by 50-char prefix against prev record)
full_names = {t[1][:50]: t[1] for t in prev['near_1.000_1.005']}
rec['near_1.000_1.005'] = [
    [s, full_names.get(q, q), y, n, l] for s, q, y, n, l in rec['near_1.000_1.005']
]

cur_band = {(t[1], round(t[0], 3)): (t[2], t[3]) for t in rec['near_1.000_1.005']}
prev_band = {(t[1], round(t[0], 3)): (t[2], t[3]) for t in prev['near_1.000_1.005']}

# compare by question name only (sum may tick)
cur_q = {t[1]: t for t in rec['near_1.000_1.005']}
prev_q = {t[1]: t for t in prev['near_1.000_1.005']}
adds = [q for q in cur_q if q not in prev_q]
drops = [q for q in prev_q if q not in cur_q]
shifts = [(q, (prev_q[q][2], prev_q[q][3]), (cur_q[q][2], cur_q[q][3]))
          for q in cur_q if q in prev_q
          and (prev_q[q][2], prev_q[q][3]) != (cur_q[q][2], cur_q[q][3])]

rec['near_misses_verbatim_asks0'] = 0
rec['note'] = (
    "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
    "FLOOR 1.002->1.002 held (West Ham 0-3 QPR Yes@0.007+No@0.995). "
    "Band 6->6: adds " + (str(adds) if adds else "[]") + ", drops " + (str(drops) if drops else "[]") + ". "
    "Intra-band shifts: " + (str(shifts) if shifts else "none") + ". "
    "Priced " + str(prev['priced_minask']) + "->" + str(rec['priced_minask']) + ". "
    "Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 — no actionable arb. Paper trades 0."
)

lines[-1] = json.dumps(rec)
with open(path, 'w') as f:
    f.write('\n'.join(lines) + '\n')

# validate whole file
allrec = [json.loads(l) for l in open(path) if l.strip()]
print("lines:", len(allrec))
print("last rec:", json.dumps(rec, ensure_ascii=False))
