import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    print("best-ask (min) totals, 10 lowest:")
    for t, q, ya, na, liq in rows[:10]:
        flag = "<<< BRACKET" if t < 1.0 else ""
        print(f"  {t:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q} {flag}")

asyncio.run(supp())
