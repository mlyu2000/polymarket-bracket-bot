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

    brackets = []
    near = []
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
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    brackets.sort()
    near.sort()
    return markets, brackets, near, priced

markets, brackets, near, priced = asyncio.run(scan())
print(f"MARKETS: {len(markets)} | priced pairs: {priced}")
print(f"MIN-ASK BRACKETS (<1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets[:10]:
    print(f"  sum={t:.4f} | Yes@{yp:.4f} No@{np_:.4f} | liq={liq} | {q}")
print(f"MIN-ASK NEAR-MISSES (<=1.005): {len(near)}")
for t, q, yp, np_, liq in near[:10]:
    print(f"  sum={t:.4f} | Yes@{yp:.4f} No@{np_:.4f} | liq={liq} | {q}")
