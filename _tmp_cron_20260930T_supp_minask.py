import asyncio, logging, time
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
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np <= 0 or yp >= 1.0 or np >= 1.0:
            continue
        priced += 1
        total = yp + np
        rows.append((total, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"📐 TRUE min-ask floor scan: {priced} priced pairs")
print(f"Pairs with true sum < 1.00: {sum(1 for r in rows if r[0] < 1.00)}")
print(f"Pairs with true sum <= 1.005 (near-miss): {sum(1 for r in rows if r[0] <= 1.005)}")
print("Top 8 lowest true sums:")
for total, q, yp, np, liq in rows[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")
