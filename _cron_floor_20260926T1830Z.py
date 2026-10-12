import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            priced += 1
            rows.append((yp + np, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

n, priced, rows = asyncio.run(scan())
print(f"markets={n} priced={priced}")
print("TRUE-FLOOR top 8 (min-of-asks):")
for t, q, yp, np, liq in rows[:8]:
    flag = "BRACKET" if t < 1.0 else "near" if t <= 1.005 else "     "
    print(f"  {t:.4f} {flag} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
