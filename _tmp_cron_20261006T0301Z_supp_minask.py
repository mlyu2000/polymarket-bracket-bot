import asyncio, logging
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
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        t = ya + na
        ydepth = sum(float(a['size']) for a in yb.asks if float(a['price']) <= ya + 0.001)
        ndepth = sum(float(a['size']) for a in nb.asks if float(a['price']) <= na + 0.001)
        priced += 1
        rows.append((t, m.question[:60], ya, na, m.liquidity, ydepth, ndepth))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print("top10 by min-ask sum:")
    for t, q, ya, na, liq, yd, nd in rows[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq:.0f} depth={yd:.0f}/{nd:.0f} | {q}")
    below = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"true brackets (sum<1.0): {len(below)}")
    for t, q, ya, na, liq, yd, nd in below:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq:.0f} depth={yd:.0f}/{nd:.0f} | {q}")
    print(f"true near-misses (1.0..1.005): {len(nm)}")
    for t, q, ya, na, liq, yd, nd in nm[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq:.0f} depth={yd:.0f}/{nd:.0f} | {q}")

asyncio.run(supp())
