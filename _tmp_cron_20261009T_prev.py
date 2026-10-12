import json

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
r = json.loads(lines[-1])
print("prev record:", r['ts_utc'])
print("best_ask_floor:", r['best_ask_floor'])
print("priced_minask:", r['priced_minask'])
print("detector_opps:", r['detector_opps'])
print("paper_trades:", r['paper_trades'])
print("band size:", len(r['near_1.000_1.005']))
for x in r['near_1.000_1.005']:
    print("  ", x)
print("total records:", len(lines))
