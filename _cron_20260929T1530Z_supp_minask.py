import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    res = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            res.append((yp + np, m.question[:55], yp, np, m.liquidity))
    res.sort()
    return len(markets), len(res), res

n, priced, rows = asyncio.run(scan())
print(f"markets={n} priced={priced}")
print("TRUE best-ask floor (top 10):")
for total, q, yp, np, liq in rows[:10]:
    print(f"  {total:.4f} | Y@{yp:.3f} N@{np:.3f} | liq={liq:,.0f} | {q}")
print(f"count sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
