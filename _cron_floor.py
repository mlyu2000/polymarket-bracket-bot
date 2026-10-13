import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    print(f"SCAN: {len(markets)} markets in {scan_time:.1f}s")
    print(f"MIN-ASK FLOOR (min of ALL asks, both sides):")
    for total, q, yp, np, liq in rows[:5]:
        print(f"  {total:.4f} | Yes@{yp:.4f} No@{np:.4f} | {q}")
    print(f"TOTALS: <=1.005={sum(1 for r in rows if r[0]<=1.005)} <=1.010={sum(1 for r in rows if r[0]<=1.010)} <=1.020={sum(1 for r in rows if r[0]<=1.020)} <=1.030={sum(1 for r in rows if r[0]<=1.030)} <=1.050={sum(1 for r in rows if r[0]<=1.050)}")

asyncio.run(scan())
