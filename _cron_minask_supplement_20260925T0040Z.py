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
    near = []
    priced = 0
    best_floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            if best_floor is None or total < best_floor[0]:
                best_floor = (total, m.question[:50], yes_price, no_price, m.liquidity)
            if total <= 1.005:
                near.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    near.sort()
    return priced, near, best_floor

priced, near, best_floor = asyncio.run(scan())
print(f"Priced markets: {priced}")
print(f"Best-ask (min) near-misses (<=1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if best_floor:
    print(f"Global best-ask floor: {best_floor[0]:.4f} | Yes@{best_floor[2]:.3f} No@{best_floor[3]:.3f} | {best_floor[1]}")
