import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    floor = None
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        if floor is None or total < floor:
            floor = total
        if total <= 1.005:
            near.append((total, m.question[:60], yp, np, m.liquidity))
    near.sort()
    print(f"priced markets (both sides): {priced} / {len(markets)}")
    print(f"global min sum (best asks): {floor:.4f}")
    brackets = [x for x in near if x[0] < 1.0]
    print(f"best-ask brackets (sum<1.0): {len(brackets)}")
    for b in brackets:
        print(f"  BRACKET {b[0]:.4f} | Yes@{b[2]:.3f} No@{b[3]:.3f} | liq={b[4]} | {b[1]}")
    print(f"near-misses (1.000-1.005, min-ask): {len([x for x in near if x[0] >= 1.0])}")
    for total, q, yp, np, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
