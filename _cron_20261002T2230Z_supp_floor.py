import asyncio, logging, time
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
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print(f"BRACKETS best-ask sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"near-misses best-ask <=1.005: {sum(1 for r in rows if 1.0 <= r[0] <= 1.005)}")
    print("floor (top 6 lowest sums):")
    for s, q, yp, np, liq in rows[:6]:
        print(f"  {s:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(supp())
