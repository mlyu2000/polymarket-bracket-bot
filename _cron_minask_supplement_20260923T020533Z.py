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

    totals = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        totals.append((total, m.question[:55], ya, na, m.liquidity))
        if total < 1.0:
            brackets.append((total, m.question[:55], ya, na, m.liquidity))

    totals.sort()
    return totals, brackets

totals, brackets = asyncio.run(scan())
print(f"Markets with usable min-asks: {len(totals)}")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("Top 10 closest (lowest min-ask sums):")
for t, q, yp, np_, liq in totals[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
