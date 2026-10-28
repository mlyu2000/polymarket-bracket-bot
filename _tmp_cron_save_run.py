"""One-shot: scan Polymarket, save supp_data.json + scan_out.txt, append history line.
Uses min-ask (source of truth) for near-misses, matching the detector's logic.
"""
import asyncio, json, time, datetime, os
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

TS = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

async def run():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_min = []      # min-ask near-misses (<=1.005)  — source of truth
    near_asks0 = 0     # asks[0] artifact count
    tiers = {"le1.005": 0, "le1.010": 0, "le1.020": 0, "le1.050": 0, "lt1.000": 0}
    yes_only = no_only = balanced = empty = 0
    floors = []

    for m, (yb, nb) in zip(markets, all_books):
        # bracket detection (detector uses min-ask, net_edge >= MIN_PROFIT_MARGIN)
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append({
                "q": m.question[:60], "yes": opp.yes_price, "no": opp.no_price,
                "sum": opp.total_cost, "edge": opp.net_edge,
                "shares": opp.max_shares, "liq": m.liquidity,
            })
            paper.execute(opp)
            continue

        if not yb or not nb or not yb.asks or not nb.asks:
            empty += 1
            continue

        y_min = min(yb.asks, key=lambda a: float(a["price"]))
        n_min = min(nb.asks, key=lambda a: float(a["price"]))
        yp = float(y_min["price"]); np = float(n_min["price"])
        total = yp + np
        floors.append(total)

        if total <= 1.005:
            near_min.append({"total": round(total,3), "q": m.question[:60],
                              "yes": yp, "no": np, "liq": m.liquidity})
        for k, thr in [("le1.005",1.005),("le1.010",1.010),("le1.020",1.020),("le1.050",1.050)]:
            if total <= thr:
                tiers[k] += 1
        if total < 1.0:
            tiers["lt1.000"] += 1

        # yes/no only classification
        if yp < 0.02 and np > 0.98:
            yes_only += 1
        elif np < 0.02 and yp > 0.98:
            no_only += 1
        else:
            balanced += 1

        # asks[0] artifact diagnostic
        yp0 = float(yb.asks[0]["price"]); np0 = float(nb.asks[0]["price"])
        if yp0 + np0 <= 1.005:
            near_asks0 += 1

    floor = min(floors) if floors else 99.0
    result = {
        "ts": TS,
        "markets": len(markets),
        "scan_time": round(scan_time, 1),
        "brackets": len(opps),
        "floor_min_ask": round(floor, 3),
        "two_sided": balanced,
        "not_bracketable": yes_only + no_only,
        "yes_only": yes_only,
        "no_only": no_only,
        "empty_books": empty,
        "near_miss_verbatim_asks0": near_asks0,
        "near_misses_min_le_1.005": len(near_min),
        "balanced_near_le_1.005": 0,  # placeholder; see below
        "tiers": tiers,
        "leader": [round(floor,3), near_min[0]["q"] if near_min else "n/a",
                   near_min[0]["yes"] if near_min else 0,
                   near_min[0]["no"] if near_min else 0,
                   near_min[0]["liq"] if near_min else 0],
        "top12_min_ask": near_min[:12],
        "near_miss_artifact_note": "asks[0] is worst ask (DESC-sorted CLOB /book); verbatim near-miss block always 0; min-ask diag is source of truth",
    }

    # balanced near-misses: both yes and no >= 0.02 (not yes_only/no_only)
    balanced_near = [nm for nm in near_min
                     if 0.02 <= nm["yes"] <= 0.98 and 0.02 <= nm["no"] <= 0.98]
    result["balanced_near_le_1.005"] = len(balanced_near)

    os.makedirs("runs", exist_ok=True)
    supp_path = f"runs/_tmp_cron_{TS}_supp_data.json"
    with open(supp_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    # scan_out.txt
    out_path = f"runs/_tmp_cron_{TS}_scan_out.txt"
    with open(out_path, "w") as f:
        f.write(f"# Bracket scan {TS}\n")
        f.write(f"markets={result['markets']} scan_time={result['scan_time']}s\n")
        f.write(f"brackets={result['brackets']}\n")
        f.write(f"near_misses_le_1.005(min-ask)={result['near_misses_min_le_1.005']}\n")
        f.write(f"near_misses_verbatim_asks0={result['near_miss_verbatim_asks0']}\n")
        f.write(f"floor={result['floor_min_ask']}\n")
        f.write(f"two_sided={result['two_sided']}\n")
        f.write(f"tiers={json.dumps(result['tiers'])}\n")

    # append to history jsonl
    hist_line = {
        "ts": TS,
        "markets": result["markets"],
        "scan_time": result["scan_time"],
        "brackets": result["brackets"],
        "floor": result["floor_min_ask"],
        "near_miss_verbatim_asks0": result["near_miss_verbatim_asks0"],
        "near_misses_min_le_1.005": result["near_misses_min_le_1.005"],
        "balanced_near_le_1.005": result["balanced_near_le_1.005"],
        "two_sided": result["two_sided"],
        "not_bracketable": result["not_bracketable"],
        "tiers": result["tiers"],
    }
    with open("results/cron_scan_history.jsonl", "a") as f:
        f.write(json.dumps(hist_line) + "\n")

    # console output matching the original script format
    print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
    print(f"✅ BRACKETS (sum < 1.00): {result['brackets']}")
    for o in result.get("brackets_detail", []):
        print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
    # re-print opps from the scan
    return result, opps

result, opps = asyncio.run(run())
print(f"\n✅ BRACKETS (sum < 1.00): {len(opps)}")
for o in opps:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005, min-ask CORRECT): {result['near_misses_min_le_1.005']}")
for nm in result['top12_min_ask'][:5]:
    print(f"  {nm['total']:.3f} | Yes@{nm['yes']:.3f} No@{nm['no']:.3f} | {nm['q']}")
print(f"📉 Near-misses (≤1.005, asks[0] ARTIFACT): {result['near_miss_verbatim_asks0']}")
print(f"📁 Saved: runs/_tmp_cron_{TS}_supp_data.json + scan_out.txt")
print(f"📜 Appended to results/cron_scan_history.jsonl")
