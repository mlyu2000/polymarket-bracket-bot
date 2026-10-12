import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            sums.append((yes_min + no_min, m.question[:50], yes_min, no_min, m.liquidity))
    sums.sort()
    return sums

sums = asyncio.run(scan())
print(f"Markets with both books priced: {len(sums)}")
print(f"True floor (min-ask sum): {sums[0][0]:.4f}" if sums else "no data")
print("Top 8 lowest min-ask sums:")
for total, q, yp, np, liq in sums[:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"Count sum<1.000: {sum(1 for s in sums if s[0] < 1.0)}")
print(f"Count sum<=1.005: {sum(1 for s in sums if s[0] <= 1.005)}")
