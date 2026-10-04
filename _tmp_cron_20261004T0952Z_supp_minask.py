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
        priced += 1
        yp = float(best_ask(yb)["price"])
        np = float(best_ask(nb)["price"])
        total = yp + np
        if floor is None or total < floor:
            floor = total
            floor_q = m.question[:60]
            floor_liq = m.liquidity
            floor_yp, floor_np = yp, np
        if total < 1.0:
            opp = detector.detect(m, yb, nb)
            brackets.append((total, m.question[:60], yp, np, m.liquidity, bool(opp)))
        elif total <= 1.005:
            near.append((round(total, 4), m.question[:50], yp, np, m.liquidity))

    near.sort()
    print(f"elapsed {el:.1f}s | markets {len(markets)} | both-sides-priced {priced}")
    print(f"BRACKETS (min-ask sum<1.00): {len(brackets)}")
    for b in brackets:
        print("  ", b)
    print(f"floor sum: {floor:.3f} | {floor_q} | Yes@{floor_yp:.3f} No@{floor_np:.3f} | liq {floor_liq}")
    print(f"near-misses (<=1.005): {len(near)}")
    for n in near:
        print("  ", n)

    out = {
        "ts": "20261004T0952Z",
        "markets": len(markets),
        "priced": priced,
        "brackets": brackets,
        "floor": floor,
        "floor_q": floor_q,
        "near": near,
    }
    with open("runs/_tmp_cron_20261004T0952Z_supp_data.json", "w") as f:
        json.dump(out, f, default=str)

asyncio.run(scan())
