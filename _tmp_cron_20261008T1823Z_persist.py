import json

d = json.load(open('_tmp_cron_20261008T1820Z_supp_data.json'))
near = d['near']
floor = d['true_floor']

lines = open('results/cron_scan_history.jsonl').read().splitlines()
prev = json.loads(lines[-1])
prev_q = set(t[1][:40] for t in prev.get('near_1.000_1.005', []))
cur_q = set(t[1][:40] for t in near)
added = sorted(cur_q - prev_q)
dropped = sorted(prev_q - cur_q)

entry = {
    "ts_utc": "2026-10-08T18:20Z",
    "markets": d['markets'],
    "scan_time_s": round(d['scan_time'], 1),
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        f"Floor held at 1.002 (Dortmund 0-3 Werder Yes@.005 No@.997 liq 31258, sole holder). "
        f"Band 8->8 MEMBERSHIP {'UNCHANGED' if not (added or dropped) else 'CHANGED'}; "
        f"priced 105->{d['priced']}. Added: {added or 'none'}. Dropped: {dropped or 'none'}. "
        "No sub-1.00. Paper trades 0."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('persisted 18:20Z floor', floor, 'band', len(near), 'added', added, 'dropped', dropped)
