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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        rows.append((total, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    print(f"Markets with priced books (min-ask method): {priced}/{len(markets)}")
    print("FLOOR (8 lowest sums, best-ask = min of asks):")
    for total, q, yp, np, liq in rows[:8]:
        flag = "BRACKET<1.000" if total < 1.0 else ("near<=1.005" if total <= 1.005 else "")
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q} {flag}")
    cnt_below = sum(1 for r in rows if r[0] < 1.0)
    cnt_near = sum(1 for r in rows if 1.0 <= r[0] <= 1.005)
    print(f"SUMMARY: {cnt_below} sums <1.000 | {cnt_near} sums in [1.000,1.005]")

asyncio.run(scan())
