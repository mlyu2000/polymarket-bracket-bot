import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    # Near-misses computed with BEST ask (min price), matching detector.py logic
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            priced += 1
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np, m.liquidity))
    near.sort()
    return len(markets), priced, near

markets, priced, near = asyncio.run(scan())
print(f"BEST-ASK near-misses (<=1.005): {len(near)} of {priced} priced markets ({markets} total)")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
