import json
prev = json.load(open('_tmp_cron_20261008T1743Z_supp_data.json'))
cur = json.load(open('_tmp_cron_20261008T1758Z_supp_data.json'))
print("prev: priced", prev['priced'], "floor", prev['true_floor'], "band", len(prev['near']))
print("cur : priced", cur['priced'], "floor", cur['true_floor'], "band", len(cur['near']))
pb = {q for _, q, _, _, _ in prev['near']}
cb = {q for _, q, _, _, _ in cur['near']}
print("left band:", sorted(pb - cb))
print("joined band:", sorted(cb - pb))
