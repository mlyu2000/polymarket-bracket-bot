import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"min-ask sums computed: {len(rows)}")
below1 = [r for r in rows if r[0] < 1.0]
le1005 = [r for r in rows if r[0] <= 1.005]
print(f"sum<1.000: {len(below1)} | sum<=1.005: {len(le1005)}")
for t, q, yp, np, liq in rows[:8]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
