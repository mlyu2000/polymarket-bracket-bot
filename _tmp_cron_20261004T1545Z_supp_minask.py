import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    print("floor (best min-sum):")
    for r in rows[:10]:
        total, q, yp, np, liq = r
        flag = " <1.005" if total <= 1.005 else ""
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}{flag}")
    n5 = sum(1 for r in rows if r[0] <= 1.005)
    n0 = sum(1 for r in rows if r[0] < 1.000)
    print(f"count <=1.005: {n5} | count <1.000: {n0}")

asyncio.run(scan())
