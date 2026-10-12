import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            best.append((ya + na, m.question[:60], ya, na, m.liquidity))
    best.sort()
    return priced, best

priced, best = asyncio.run(scan())
under1 = [b for b in best if b[0] < 1.0]
nm = [b for b in best if 1.0 <= b[0] <= 1.005]
print(f"Markets with priced books: {priced}")
print(f"TRUE brackets (min-sum < 1.00): {len(under1)}")
for t, q, ya, na, liq in under1[:10]:
    print(f"  sum={t:.4f} Yes@{ya:.3f} No@{na:.3f} liq={liq} | {q}")
print(f"TRUE near-misses (1.00 <= sum <= 1.005): {len(nm)}")
for t, q, ya, na, liq in nm[:10]:
    print(f"  sum={t:.4f} Yes@{ya:.3f} No@{na:.3f} liq={liq} | {q}")
print("Overall best sums (top 5):")
for t, q, ya, na, liq in best[:5]:
    print(f"  sum={t:.4f} | {q[:50]}")
