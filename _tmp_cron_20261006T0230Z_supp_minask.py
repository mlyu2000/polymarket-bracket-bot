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

    both_sides = 0
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            both_sides += 1
            y = min(float(a['price']) for a in yes_book.asks)
            n = min(float(a['price']) for a in no_book.asks)
            sums.append((y + n, m.question[:55], y, n, m.liquidity))
    sums.sort()
    return len(markets), both_sides, sums

n, both, sums = asyncio.run(scan())
print(f"markets={n} both_sides_priced={both} priced_pairs={len(sums)}")
print(f"FLOOR (min sum) = {sums[0][0]:.4f}")
band = [s for s in sums if s[0] <= 1.005]
print(f"band <=1.005: {len(band)}")
for total, q, y, n_, liq in band[:8]:
    print(f"  {total:.4f} | yes={y:.3f} no={n_:.3f} | liq={liq} | {q}")
print("top5 sums:")
for total, q, y, n_, liq in sums[:5]:
    print(f"  {total:.4f} | yes={y:.3f} no={n_:.3f} | liq={liq} | {q}")
