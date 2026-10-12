import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        first = float(yb.asks[0]['price']) + float(nb.asks[0]['price'])
        tot = ya + na
        priced += 1
        rows.append((tot, m.question[:60], ya, na, m.liquidity, first))
    rows.sort()
    print(f"priced markets: {priced}")
    print("TRUE-BEST-ASK totals (min over asks), 13 closest to sub-1.00:")
    for tot, q, ya, na, liq, first in rows[:13]:
        flag = " <-- BRACKET(sum<1)" if tot < 1.0 else ""
        print(f"  {tot:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}{flag}")
    under = [r for r in rows if r[0] < 1.0]
    print(f"markets with true best-ask sum < 1.00: {len(under)}")

asyncio.run(supp())
