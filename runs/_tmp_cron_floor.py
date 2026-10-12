import asyncio, logging, time, json, sys
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    two_sided = []   # (min_total, question, yp, np, liq)
    yes_only = 0
    no_only = 0
    empty = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        y_asks = yes_book.asks if yes_book else None
        n_asks = no_book.asks if no_book else None
        if y_asks and n_asks:
            yp = min(float(a["price"]) for a in y_asks)
            np_ = min(float(a["price"]) for a in n_asks)
            if yp > 0 and np_ > 0 and yp < 1.0 and np_ < 1.0:
                two_sided.append((yp + np_, m.question, yp, np_, m.liquidity))
            else:
                empty += 1
        elif y_asks and not n_asks:
            yes_only += 1
        elif n_asks and not y_asks:
            no_only += 1
        else:
            empty += 1

    two_sided.sort()
    floor = two_sided[0][0] if two_sided else None
    bands = {
        "<=1.005": sum(1 for t in two_sided if t[0] <= 1.005),
        "<=1.010": sum(1 for t in two_sided if t[0] <= 1.010),
        "<=1.020": sum(1 for t in two_sided if t[0] <= 1.020),
        "<=1.030": sum(1 for t in two_sided if t[0] <= 1.030),
        "<1.00": sum(1 for t in two_sided if t[0] < 1.00),
    }
    out = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "markets": len(markets),
        "scan_time": round(scan_time, 1),
        "structural": {"two_sided": len(two_sided), "yes_only": yes_only,
                       "no_only": no_only, "empty_or_invalid": empty},
        "floor": round(floor, 4) if floor else None,
        "bands": bands,
        "lowest_10": [
            {"total": round(t[0], 4), "yes": round(t[2], 4), "no": round(t[3], 4),
             "liq": t[4], "q": t[1][:70]} for t in two_sided[:10]
        ],
    }
    with open("/tmp/polybracket_floor.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

asyncio.run(scan())
