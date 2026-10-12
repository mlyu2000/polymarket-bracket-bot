import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        priced += 1
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    print(f"brackets (best-ask sum < 1.00): {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"near-misses (<=1.005): {sum(1 for r in rows if r[0] <= 1.005)}")
    print("--- top 10 lowest sums ---")
    for s, q, yp, np, liq in rows[:10]:
        print(f"  {s:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

result = asyncio.run(supp())
