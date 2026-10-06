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
    brackets_min = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yes_best = min(float(a['price']) for a in yes_book.asks)
        no_best = min(float(a['price']) for a in no_book.asks)
        total = yes_best + no_best
        if total < 1.0:
            brackets_min.append((total, m.question[:60], yes_best, no_best, m.liquidity))
        if total <= 1.005:
            results.append((total, m.question[:60], yes_best, no_best, m.liquidity))

    results.sort()
    brackets_min.sort()
    print(f"BRACKETS via min-ask (sum<1.00): {len(brackets_min)}")
    for total, q, yp, np, liq in brackets_min[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"BEST-ASK NEAR-MISS TOP (<=1.005): {len(results)}")
    for total, q, yp, np, liq in results[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if results:
        print(f"FLOOR: {results[0][0]:.4f}")

asyncio.run(scan())
