import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        rows.append((y + n, m.question[:55], y, n, m.liquidity))

    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    if rows:
        print(f"BEST (lowest sum via min-ask): {rows[0][0]:.4f}")
        print("TOP 8 lowest sums:")
        for s, q, y, n, liq in rows[:8]:
            flag = " <1.00 !!!" if s < 1.0 else ""
            print(f"  {s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq:.0f} | {q}{flag}")
        below1 = [r for r in rows if r[0] < 1.0]
        print(f"count(sum<1.00)={len(below1)}  count(sum<=1.005)={len([r for r in rows if r[0]<=1.005])}")

asyncio.run(supp())
