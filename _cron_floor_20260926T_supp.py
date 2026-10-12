import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
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
        total = yp + np
        priced += 1
        rows.append((total, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print("top-8 by best-ask sum:")
    for t, q, yp, np, liq in rows[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:,.0f} | {q}")

asyncio.run(scan())
