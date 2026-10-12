import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    print(f"MIN-ASK floor scan: {len(rows)} priced markets")
    for total, q, yp, np_, liq in rows[:10]:
        flag = ' *** BRACKET ***' if total < 1.0 else ''
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}{flag}")
    under = [r for r in rows if r[0] < 1.0]
    print(f"Brackets (min-ask sum < 1.0): {len(under)}")

asyncio.run(supp())
