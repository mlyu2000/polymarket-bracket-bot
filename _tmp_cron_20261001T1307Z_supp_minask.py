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

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            rows.append((total, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

result = asyncio.run(scan())
n_markets, n_priced, rows = result
print(f"min-ask scan: {n_markets} markets, {n_priced} priced both sides")
print(f"floor: {rows[0][0]:.4f}" if rows else "no priced books")
print("brackets (min-ask sum < 1.00):", sum(1 for r in rows if r[0] < 1.0))
print("near-misses (<=1.005):")
for total, q, yp, np_, liq in rows:
    if total <= 1.005:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
