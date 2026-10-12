import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    minsum = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np <= 0 or yp >= 1 or np >= 1:
            continue
        priced += 1
        total = yp + np
        if minsum is None or total < minsum:
            minsum = total
        if total <= 1.005 and m.liquidity > 0:
            rows.append((total, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"BEST-ASK NEAR-MISSES (sum<=1.005, liq>0): {len(rows)} of {priced} priced markets; global min sum={minsum}")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())
