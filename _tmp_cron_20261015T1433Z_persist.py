import json, os, datetime

TS = "20261015T1433Z"
SUPP = f"runs/_tmp_cron_{TS}_supp_data.json"
HIST = "results/cron_scan_history.jsonl"

with open(SUPP) as f:
    data = json.load(f)

diag = data['diag']
two_sided = data['two_sided']
markets = 500

tiers = diag['tiers']
tiers_obj = dict(tiers)
tiers_obj['two_sided'] = two_sided
tiers_obj['markets'] = markets
tiers_obj['pct_not_bracketable'] = round((1 - two_sided / markets) * 100, 1)

with open(f"runs/_tmp_cron_{TS}_tiers.json", 'w') as f:
    json.dump(tiers_obj, f, indent=2)

top = [
    {"total": t, "q": q, "yes": yp, "no": npx, "liq": liq}
    for t, q, yp, npx, liq in diag['min_asks'][:12]
]

line = {
    "ts": TS,
    "brackets": 0,
    "markets": markets,
    "two_sided": two_sided,
    "pct_not_bracketable": tiers_obj['pct_not_bracketable'],
    "tiers": tiers,
    "floor": diag['min_asks'][0][0] if diag['min_asks'] else None,
    "top12": top,
    "scan_time_verbatim": 71.0,
}
os.makedirs("results", exist_ok=True)
with open(HIST, 'a') as f:
    f.write(json.dumps(line) + "\n")

print(f"appended history line; tiers saved to runs/_tmp_cron_{TS}_tiers.json")
print(json.dumps(tiers_obj, indent=2))
