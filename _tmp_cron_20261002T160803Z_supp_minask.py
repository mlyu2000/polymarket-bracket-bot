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

    near = []
    priced = 0
    best_overall = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if best_overall is None or total < best_overall[0]:
                best_overall = (total, m.question[:60])
            if total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    return markets, priced, near, best_overall

markets, priced, near, best = asyncio.run(scan())
print(f"priced markets (min-ask): {priced}")
if best:
    print(f"global min sum: {best[0]:.4f} | {best[1]}")
print(f"near-misses <=1.005 (min-ask): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
