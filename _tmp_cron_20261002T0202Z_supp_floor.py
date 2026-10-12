import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        ya = min(yes_book.asks, key=lambda a: float(a['price']))
        na = min(no_book.asks, key=lambda a: float(a['price']))
        yp = float(ya['price']); np_ = float(na['price'])
        rows.append((yp + np_, m.question[:60], yp, np_, float(ya['size']), float(na['size']), m.liquidity))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"priced={priced}")
for t, q, yp, np_, ys, ns, liq in rows[:8]:
    print(f"  {t:.4f} | Yes@{yp:.3f}x{ys:.0f} No@{np_:.3f}x{ns:.0f} | liq={liq} | {q}")
