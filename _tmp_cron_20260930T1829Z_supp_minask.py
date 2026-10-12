import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near_misses = []
    priced = 0
    brackets_min = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            priced += 1
            if total < 1.0 and m.liquidity > 0:
                brackets_min.append((total, m.question[:50], ya, na, m.liquidity))
            elif total <= 1.005:
                near_misses.append((total, m.question[:50], ya, na, m.liquidity))
    near_misses.sort()
    brackets_min.sort()
    return priced, brackets_min, near_misses

priced, br, nm = asyncio.run(scan())
print(f"Markets with both books priced: {priced}")
print(f"TRUE brackets (best-ask min, sum<1.00, liq>0): {len(br)}")
for total, q, yp, np, liq in br[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"Near-misses (best-ask min basis, <=1.005): {len(nm)}")
for total, q, yp, np, liq in nm[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
