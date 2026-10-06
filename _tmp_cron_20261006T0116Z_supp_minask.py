import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"both-sides-priced: {priced}/{len(markets)}")
    print("--- true min-ask floor (top 8) ---")
    for t, q, y, n, lq in rows[:8]:
        flag = " <1.00" if t < 1.0 else (" <=1.005" if t <= 1.005 else "")
        print(f"  sum={t:.4f} | yes={y:.3f} no={n:.3f} | liq={lq:.0f} | {q}{flag}")
    band = [r for r in rows if r[0] <= 1.005]
    print(f"band <=1.005 count: {len(band)}")
    sub1 = [r for r in rows if r[0] < 1.0]
    print(f"true brackets (min-ask sum<1.00): {len(sub1)}")
    for t, q, y, n, lq in sub1:
        print(f"  REAL {t:.4f} | yes={y:.3f} no={n:.3f} | liq={lq:.0f} | {q}")

asyncio.run(supp())
