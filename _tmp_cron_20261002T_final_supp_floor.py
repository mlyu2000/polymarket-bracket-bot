import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return rows, time.time() - t0

rows, el = asyncio.run(supp())
priced = len(rows)
print(f"Supp best-ask floor check: {priced} priced markets in {el:.1f}s")
print(f"  min sum = {rows[0][0]:.4f}" if rows else "  no data")
print(f"  <=1.000: {sum(1 for r in rows if r[0] <= 1.0001)}")
print(f"  <=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
print(f"  <=1.01:  {sum(1 for r in rows if r[0] <= 1.01)}")
print("Top-5 closest to bracket (true best asks):")
for total, q, yp, np_, liq in rows[:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
