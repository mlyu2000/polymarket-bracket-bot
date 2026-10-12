import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
logging.basicConfig(level=logging.ERROR)

async def run():
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
        tot = ya + na
        priced += 1
        if tot <= 1.005:
            rows.append((tot, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    if rows:
        print(f"min true sum: {rows[0][0]:.4f}")
    print(f"true near-misses (<=1.005): {len(rows)}")
    for t,q,ya,na,liq in rows[:8]:
        print(f"  {t:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
asyncio.run(run())
