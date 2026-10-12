import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        total = yp + np
        priced += 1
        rows.append((total, m.question[:70], yp, np, m.liquidity))

    rows.sort()
    print(f"priced markets: {priced}")
    print("top-10 best sums (min ask Yes + min ask NO):")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"true brackets (sum<1.000): {len(brackets)}")
    near = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"near-misses (1.000-1.005): {len(near)}")
    for total, q, yp, np, liq in near[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    le1010 = [r for r in rows if r[0] <= 1.010]
    print(f"count <=1.010: {len(le1010)}")

asyncio.run(supp())
