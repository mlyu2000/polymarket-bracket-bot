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
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity <= 0:
            continue
        yes_p = min(float(a['price']) for a in yes_book.asks)
        no_p = min(float(a['price']) for a in no_book.asks)
        total = yes_p + no_p
        priced += 1
        if total <= 1.01:
            rows.append((total, m.question[:60], yes_p, no_p, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

async def main():
    return await scan()

markets, priced, rows = asyncio.run(main())
print(f"Supplement (best-ask/min): {markets} markets, {priced} with two-sided asks")
print(f"sum<=1.01: {len(rows)}")
for total, q, yp, np, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
