import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    # CLOB asks come DESC-sorted; best ask = lowest price
    return min(book.asks, key=lambda a: float(a["price"]))

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    el = time.time() - t0

    brackets = []
    near = []
    floor = None
    floor_q = None
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = float(best_ask(yb)["price"])
        np = float(best_ask(nb)["price"])
        tot = yp + np
        priced += 1
        if floor is None or tot < floor:
            floor, floor_q = tot, m.question[:70]
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, yp, np, m.liquidity, m.question[:70]))
        elif tot <= 1.005:
            near.append((tot, m.question[:60], yp, np, m.liquidity))

    brackets.sort()
    near.sort()
    print(f"MARKETS={len(markets)} PRICED={priced} ELAPSED={el:.1f}s")
    print(f"FLOOR_SUM={floor:.4f} :: {floor_q}")
    print(f"BRACKETS={len(brackets)}")
    for b in brackets:
        print(f"  SUM={b[0]:.4f} EDGE={b[1]:.4f} SHARES={b[2]} Y={b[3]:.3f} N={b[4]:.3f} LIQ={b[5]} :: {b[6]}")
    print(f"NEAR_MISSES_LE_1.005={len(near)}")
    for t, q, yp, np, liq in near[:10]:
        print(f"  {t:.4f} Y@{yp:.3f} N@{np:.3f} LIQ={liq} :: {q}")

    out = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "markets": len(markets), "priced": priced,
           "floor": floor, "floor_q": floor_q,
           "brackets": [list(b) for b in brackets],
           "near": [list(x) for x in near], "elapsed": el}
    with open(OUTJSON, "w") as f:
        json.dump(out, f)

OUTJSON = "_tmp_cron_20261004T0855Z_supp_data.json"
asyncio.run(scan())
