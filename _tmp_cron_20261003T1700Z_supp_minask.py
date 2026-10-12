import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        total = yp + np
        priced += 1
        rows.append((total, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    print(f"min-ask scan: {priced}/{len(markets)} priced in {dt:.1f}s")
    print("BEST (lowest sum) 10:")
    for total, q, yp, np, liq in rows[:10]:
        flag = "BRACKET<1.00" if total < 1.0 else ("<=1.005" if total <= 1.005 else "")
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {flag} | {q}")
    print(f"count sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")

asyncio.run(scan())
