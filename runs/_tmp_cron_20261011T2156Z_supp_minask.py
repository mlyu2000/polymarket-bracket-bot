"""True-floor supplementary: min(all asks) on both sides (CLOB asks are DESC-sorted,
asks[0] is the WORST ask). Also collects book-shape stats + tiers, persists JSON."""
import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    bands = {"le_1_005": [], "le_1_010": [], "le_1_020": [], "le_1_030": []}
    two_sided_priced = 0
    yes_only = 0
    no_only = 0
    empty = 0
    detector_opps = 0
    min_total = None
    min_market = None

    for m, (yb, nb) in zip(markets, all_books):
        if detector.detect(m, yb, nb):
            detector_opps += 1
        y_asks = yb.asks if yb is not None else None
        n_asks = nb.asks if nb is not None else None
        if y_asks and n_asks:
            two_sided_priced += 1
        elif y_asks:
            yes_only += 1
        elif n_asks:
            no_only += 1
        else:
            empty += 1
            continue
        if not y_asks or not n_asks:
            continue
        y_min = min(float(a["price"]) for a in y_asks)
        n_min = min(float(a["price"]) for a in n_asks)
        total = round(y_min + n_min, 4)
        if min_total is None or total < min_total:
            min_total = total
            min_market = {"q": m.question[:80], "yes": y_min, "no": n_min,
                          "liq": m.liquidity,
                          "y_levels": len(yb.asks), "n_levels": len(nb.asks)}
        if total <= 1.005:
            bands["le_1_005"].append({"total": total, "yes": y_min, "no": n_min,
                                      "y_lev": len(yb.asks), "n_lev": len(nb.asks),
                                      "q": m.question[:80], "liq": m.liquidity})
        elif total <= 1.010:
            bands["le_1_010"].append({"total": total, "yes": y_min, "no": n_min,
                                      "q": m.question[:60], "liq": m.liquidity})
        elif total <= 1.020:
            bands["le_1_020"].append({"total": total, "yes": y_min, "no": n_min,
                                      "q": m.question[:60], "liq": m.liquidity})
        elif total <= 1.030:
            bands["le_1_030"].append({"total": total, "yes": y_min, "no": n_min,
                                      "q": m.question[:60], "liq": m.liquidity})

    bands["le_1_005"].sort(key=lambda x: x["total"])
    bands["le_1_010"].sort(key=lambda x: x["total"])
    bands["le_1_020"].sort(key=lambda x: x["total"])
    bands["le_1_030"].sort(key=lambda x: x["total"])

    out = {
        "run": "2026-10-11T2156Z",
        "markets": len(markets),
        "scan_time_s": round(scan_time, 1),
        "brackets": detector_opps,
        "true_floor_min_ask": min_total,
        "floor_market": min_market,
        "band_le_1_005": bands["le_1_005"],
        "band_le_1_010_count": len(bands["le_1_010"]),
        "band_le_1_020_count": len(bands["le_1_020"]),
        "band_le_1_030_count": len(bands["le_1_030"]),
        "book_shape": {"two_sided_priced": two_sided_priced, "yes_only": yes_only,
                       "no_only": no_only, "empty": empty},
    }
    with open("runs/_tmp_cron_20261011T2156Z_supp_data.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

asyncio.run(main())
