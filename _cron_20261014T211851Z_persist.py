import json, re

src = "_cron_20261014_supp_out.txt"
dst = "runs/_tmp_cron_20261014T211851Z_supp_data.json"
with open(src) as f:
    text = f.read()
m = re.search(r"JSON_START\n(.*)\nJSON_END", text, re.S)
data = json.loads(m.group(1))
with open(dst, "w") as f:
    json.dump(data, f, indent=1)
print(f"wrote {dst}: {len(data['rows'])} rows, brackets={len(data['brackets'])}, tiers={data['tiers']}")
