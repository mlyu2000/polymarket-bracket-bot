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

    results = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            total = yes_min + no_min
            results.append((total, m.question[:60], yes_min, no_min, m.liquidity))
    results.sort()
    print(f"MIN-ASK cross-check: {len(results)} priced markets of {len(markets)}")
    print("Lowest 8 Yes+No best-ask sums:")
    for total, q, yp, np, liq in results[:8]:
        flag = "BRACKET<1.00" if total < 1.0 else ""
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q} {flag}")

asyncio.run(scan())
