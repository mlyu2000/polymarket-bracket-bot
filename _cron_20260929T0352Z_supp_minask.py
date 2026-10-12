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
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"elapsed={time.time()-t0:.1f}s priced={len(rows)}/{len(markets)}")
    print("TRUE-BEST-ASK TOP 10 (lowest sums):")
    for s, q, yp, np, liq in rows[:10]:
        print(f"  {s:.4f} | Y@{yp:.3f} N@{np:.3f} | liq={liq} | {q}")
    print(f"brackets(sum<1): {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"near<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    print(f"floor: {rows[0][0]:.4f}")

asyncio.run(scan())
