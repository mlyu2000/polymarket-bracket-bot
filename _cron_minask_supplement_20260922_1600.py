import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    near = []
    best = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            priced += 1
            if best is None or total < best[0]:
                best = (total, m.question[:60], ya, na, m.liquidity)
            if total <= 1.005:
                near.append((total, m.question[:60], ya, na, m.liquidity))
    near.sort()
    return priced, near, best

priced, near, best = asyncio.run(scan())
print(f"Markets priced (min-ask): {priced}")
print(f"Near-misses (<=1.005): {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if best:
    print(f"GLOBAL BEST: sum={best[0]:.3f} | Yes@{best[2]:.3f} No@{best[3]:.3f} | {best[1]}")
