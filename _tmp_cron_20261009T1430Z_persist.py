import json

TS = "2026-10-09T14:35Z"
scan = {"markets": 500, "opps": [], "near_misses": [], "scan_time": 50.7}
supp = json.load(open('_tmp_cron_20261009T1430Z_supp_data.json'))

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])
prev_band = [tuple(x) for x in prev['near_1.000_1.005']]

band = [r for r in supp['rows'] if 1.0 <= r['sum'] <= 1.005]
for r in band:
    r['q'] = r['q'][:60]  # align truncation with history rows (m.question[:60])
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
cur_map = {(round(r['sum'], 3), r['q']): (r['yes'], r['no']) for r in band_u}
prev_map = {(round(t[0], 3), t[1]): (t[2], t[3]) for t in prev_band}
shifts = []
for k in sorted(cur_set & prev_set):
    if prev_map[k] != cur_map[k]:
        shifts.append((k[1], prev_map[k], cur_map[k]))
brackets = [r for r in supp['rows'] if r['sum'] < 1.0]

floor = round(supp['floor'], 3) if supp['floor'] is not None else None
prev_floor = prev['best_ask_floor']
if floor == prev_floor:
    trend = "held"
elif floor < prev_floor:
    trend = "fell"
else:
    trend = "rose"

def fmt(s):
    return f"{s[0]}@{s[1]:.3f}" if isinstance(s, tuple) else str(s)

note = (
    f"verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
    f"FLOOR {prev_floor}->{floor} {trend}. "
    f"Band {len(prev_band)}->{len(band_u)}: adds {[fmt(a) for a in adds]}, drops {[fmt(d) for d in drops]}. "
    f"Intra-band shifts: {shifts if shifts else 'none'}. "
    f"Priced {prev['priced_minask']}->{supp['parsed']}. "
    f"Detector opportunities: {len(scan['opps'])}. "
    f"True brackets (min-ask sum<1.00): {len(brackets)} — no actionable arb. Paper trades 0."
)

row = {
    "ts_utc": TS,
    "markets": scan["markets"],
    "scan_time_s": scan["scan_time"],
    "brackets_verbatim": len(scan["opps"]),
    "near_misses_verbatim_asks0": len(scan["near_misses"]),
    "priced_minask": supp["parsed"],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "detector_opps": len(scan["opps"]),
    "paper_trades": 0,
    "note": note,
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(note)
print("rows now:", len(lines) + 1)
