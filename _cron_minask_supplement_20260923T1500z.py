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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            rows.append((yes_price + no_price, m.question[:55], yes_price, no_price, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"min-ask sums computed for {len(rows)} markets")
brackets = [r for r in rows if r[0] < 1.0]
print(f"min-ask BRACKETS (<1.0): {len(brackets)}")
for s, q, yp, np_, liq in brackets[:10]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("FLOOR (10 lowest min-ask sums):")
for s, q, yp, np_, liq in rows[:10]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
