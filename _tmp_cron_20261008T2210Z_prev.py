import json
prev = [json.loads(l) for l in open('results/cron_scan_history.jsonl')]
last = prev[-1]
print("PREV ts:", last['ts_utc'], "priced:", last['priced_minask'], "floor:", last['best_ask_floor'])
band = sorted({q for _, q, *_ in last['near_1.000_1.005']})
print("PREV band size:", len(band))
for t, q, *rest in last['near_1.000_1.005']:
    print(f"  {t:.3f} {q}")
cur = json.load(open('_tmp_cron_20261008T2210Z_supp_data.json'))
curband = {q for _, q, *_ in cur['near']}
print("CUR priced:", cur['priced'], "floor:", cur['true_floor'], "band size:", len(curband))
print("ADDED:", sorted(curband - set(band)))
print("DROPPED:", sorted(set(band) - curband))
for t, q, *rest in cur['near']:
    print(f"  {t:.3f} {q}")
