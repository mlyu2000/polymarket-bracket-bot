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

    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yes_best = min(float(a['price']) for a in yes_book.asks)
        no_best = min(float(a['price']) for a in no_book.asks)
        totals.append((yes_best + no_best, m.question[:60], m.liquidity))

    totals.sort()
    priced = len(totals)
    print(f"PRICED MARKETS: {priced}")
    print("TOP 8 LOWEST BEST-ASK TOTALS:")
    for t, q, liq in totals[:8]:
        print(f"  {t:.4f} | liq={liq} | {q}")
    print(f"FLOOR: {totals[0][0]:.4f}")

asyncio.run(scan())
