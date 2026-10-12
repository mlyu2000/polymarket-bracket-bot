import asyncio, logging
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            rows.append((total, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    print(f"Markets fetched: {len(markets)} | priced (both books have asks): {priced}")
    print("Top 10 closest brackets by BEST ask (sum ascending):")
    for total, q, yp, np_, liq in rows[:10]:
        flag = " <<< BRACKET" if total < 1.0 else ""
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}{flag}")
    n_lt1 = sum(1 for r in rows if r[0] < 1.0)
    n_le1005 = sum(1 for r in rows if r[0] <= 1.005)
    print(f"Count best-ask sum < 1.00: {n_lt1} | <= 1.005: {n_le1005}")

asyncio.run(scan())
