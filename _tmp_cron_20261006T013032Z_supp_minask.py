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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not m.active or m.closed or m.liquidity <= 0:
            continue
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np <= 0 or yp >= 1.0 or np >= 1.0:
            continue
        priced += 1
        total = yp + np
        if total <= 1.005:
            near.append((total, m.question[:55], yp, np, m.liquidity))

    near.sort()
    return len(markets), priced, near

res = asyncio.run(scan())
print(f"Markets: {res[0]}, priced: {res[1]}")
print(f"Near-misses (min-ask, <=1.005): {len(res[2])}")
for total, q, yp, np, liq in res[2][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
