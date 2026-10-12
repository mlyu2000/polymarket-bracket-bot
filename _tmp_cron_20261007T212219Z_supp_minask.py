import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp+np_, m.question[:60], yp, np_, m.liquidity))
            priced += 1
    rows.sort()
    return len(markets), priced, rows

n, priced, rows = asyncio.run(scan())
print(f"markets={n} priced={priced}")
print(f"sum<1.00 (true brackets): {sum(1 for r in rows if r[0] < 1.0)}")
print(f"sum<=1.005 (near-misses): {sum(1 for r in rows if r[0] <= 1.005)}")
print("top 8 lowest sums:")
for t, q, yp, np_, liq in rows[:8]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
