import json, re, time

RUN = "20261006T0730Z"

# Parse min-ask supp output
top = []
with open(f"_tmp_cron_{RUN}_supp_out.txt") as f:
    lines = f.read().strip().splitlines()
priced = int(re.search(r"over (\d+) priced", lines[0]).group(1))
brackets_minask = int(re.search(r"brackets\(sum<1\.00\)=(\d+)", lines[-1]).group(1))
for ln in lines[1:-1]:
    m = re.match(r"\s+([\d.]+) \| Yes@([\d.]+) No@([\d.]+) \| liq=([\d.]+) \| (.*)$", ln)
    s, y, n, liq, q = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    top.append({"sum": round(float(s), 4), "q": q, "yes": float(y), "no": float(n), "liq": float(liq)})

floor = top[0]["sum"]
band = [t for t in top if 1.0 <= t["sum"] <= 1.005]

run_json = {"markets": 500, "priced": priced, "floor": floor,
            "brackets_minask": brackets_minask, "band_minask": len(band), "top": top}
with open(f"runs/scan_{RUN}.json", "w") as f:
    json.dump(run_json, f, indent=1)

latest = {"run": RUN, "markets": 500, "scan_time_s": 43.9,
          "brackets_detector": 0, "bracket_opps": [],
          "near_misses_verbatim_asks0": 0, "near_misses_verbatim": [],
          "brackets_true_minask": brackets_minask,
          "near_misses_true_minask": len(band),
          "best_ask_floor": floor, "priced_markets": priced,
          "top_true_sums": top}
with open("runs/scan_latest.json", "w") as f:
    json.dump(latest, f, indent=1)

floor_json = {"run": RUN, "markets": 500, "brackets_minask": brackets_minask,
              "band_1.000_1.005": len(band), "floor": floor, "priced": priced, "top": top}
with open("runs/scan_latest_floor.json", "w") as f:
    json.dump(floor_json, f, indent=1)

with open("runs/scan_latest.out", "w") as f:
    f.write("Scan: 500 markets in 43.9s\nBRACKETS (detector, net_edge>=margin): 0\n"
            "Near-misses verbatim asks[0] (<=1.005): 0\n"
            f"Min-ask floor: {floor} over {priced} priced markets; brackets(sum<1.00)={brackets_minask}; band<=1.005={len(band)}\n")

hist = {"ts": "2026-10-06T07:30Z", "markets": 500, "scan_time_s": 43.9, "brackets": 0,
        "brackets_true_minask": brackets_minask, "near_misses_minask": len(band),
        "best_ask_floor": floor, "priced_markets": priced}
with open("runs/scan_history.jsonl", "a") as f:
    f.write(json.dumps(hist) + "\n")

print("persisted:", RUN, "floor", floor, "priced", priced, "band", len(band), "brackets", brackets_minask)
