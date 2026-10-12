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
    best_floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if best_floor is None or total < best_floor[0]:
                best_floor = (total, m.question[:60])
            if total <= 1.005:
                near.append((total, m.question[:60], yp, np, m.liquidity))
    near.sort()
    return len(markets), near, best_floor

n, near, floor = asyncio.run(scan())
print(f"markets scanned: {n}")
print(f"true floor (min-ask sum): {floor[0]:.4f} | {floor[1]}" if floor else "no priced books")
print(f"near-misses <=1.005 (min ask): {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
