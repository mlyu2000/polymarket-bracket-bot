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

    priced = 0
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if m.liquidity > 0:
            priced += 1
        if total <= 1.005:
            near.append((round(total, 4), m.question[:60], yp, np_, round(m.liquidity), m.liquidity > 0))
    near.sort()
    print(f"priced markets (liq>0, both asks): {priced}")
    print(f"near-misses (<=1.005, best-ask): {len(near)}")
    for t, q, yp, np_, liq, passliq in near:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | passMINLIQ={passliq} | {q}")

asyncio.run(scan())
