import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if total < 1.0:
                brackets.append((total, m.question[:60], yp, np_, m.liquidity))
            elif total <= 1.005:
                best.append((total, m.question[:50], yp, np_, m.liquidity))
    brackets.sort()
    best.sort()
    print(f"[min-ask correction] priced books: {priced}/{len(markets)}")
    print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for total, q, yp, np_, liq in brackets[:10]:
        print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"Near-misses ≤1.005 (min-ask): {len(best)}")
    for total, q, yp, np_, liq in best[:5]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(supp())
