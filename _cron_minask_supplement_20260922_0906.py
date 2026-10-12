import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
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
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"min-ask floor check over {priced}/{len(markets)} markets with two-sided asks")
    for t, q, ya, na, liq in rows[:8]:
        flag = ' <<< SUM<1.00' if t < 1.0 else ''
        print(f"  {t:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq:,.0f} | {q}{flag}")
    hits = [r for r in rows if r[0] < 1.0]
    print(f"min-ask sum<1.00 count: {len(hits)}")

asyncio.run(check())
