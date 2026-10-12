import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if floor is None or total < floor[0]:
            floor = (total, m.question[:60], yp, np_, m.liquidity)
        if total <= 1.005:
            near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    return len(markets), floor, near

n, floor, near = asyncio.run(scan())
print(f"markets={n}")
if floor:
    print(f"TRUE FLOOR (min-ask): sum={floor[0]:.3f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | liq={floor[4]} | {floor[1]}")
print(f"min-ask near-misses (<=1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
