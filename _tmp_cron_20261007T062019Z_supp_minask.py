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

    near = []
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))

    near.sort()
    brackets.sort()
    print(f"priced markets (min-ask basis): {priced}")
    print(f"true brackets (sum<1.00): {len(brackets)}")
    for t, q, yp, np_, liq in brackets[:10]:
        print(f"  BRACKET {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"near-misses (<=1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    all_totals = [b[0] for b in brackets] + [n[0] for n in near]
    print(f"floor: {min(all_totals) if all_totals else 'n/a'}")

asyncio.run(scan())
