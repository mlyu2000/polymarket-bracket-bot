import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

TS = "20261012T071830Z"

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []          # (total, question, yp, np, liq)
    brackets = []
    detector_hits = 0
    yes_only = no_only = empty = both = 0

    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            detector_hits += 1
            brackets.append((opp.total_cost, m.question[:60], opp.yes_price, opp.no_price, m.liquidity))
            continue
        y_ok = bool(yb and yb.asks)
        n_ok = bool(nb and nb.asks)
        if y_ok and n_ok:
            both += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
        elif y_ok:
            yes_only += 1
        elif n_ok:
            no_only += 1
        else:
            empty += 1

    rows.sort()
    brackets.sort()
    floor = rows[0] if rows else None
    tiers = {}
    for thr in (1.005, 1.01, 1.02, 1.03, 1.05, 1.1):
        tiers[f"{thr}"] = sum(1 for r in rows if r[0] <= thr)

    data = {
        "ts": TS,
        "markets": len(markets),
        "priced": both,
        "scan_time": round(scan_time, 1),
        "one_sided": {"yes_only": yes_only, "no_only": no_only, "empty": empty, "both": both},
        "floor": round(floor[0], 4) if floor else None,
        "floor_q": floor[1] if floor else None,
        "floor_yes": floor[2] if floor else None,
        "floor_no": floor[3] if floor else None,
        "floor_liq": floor[4] if floor else None,
        "band": [list(r[:5]) for r in rows if r[0] <= 1.005],
        "brackets": [list(b[:5]) for b in brackets],
        "detector_opps": detector_hits,
        "best_gross_edge": round(1.0 - floor[0], 4) if floor else None,
        "tiers": tiers,
        "top12": [[round(r[0], 4), r[1], r[2], r[3], round(r[4], 2)] for r in rows[:12]],
    }

    with open(f"runs/_tmp_cron_{TS}_supp_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"markets={len(markets)} priced_pairs={both} detector_hits={detector_hits} scan={scan_time:.1f}s")
    print(f"one_sided: yes_only={yes_only} no_only={no_only} empty={empty}")
    if floor:
        print(f"TRUE FLOOR: {floor[0]:.4f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | liq={floor[4]:.0f} | {floor[1]}")
    print(f"tiers: {tiers}")
    print("top12 (min-ask sums):")
    for r in rows[:12]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")
    if brackets:
        print(f"DETECTOR BRACKETS (sum<1.00): {len(brackets)}")
        for b in brackets:
            print(f"  {b[0]:.4f} | {b[1]}")

asyncio.run(scan())
