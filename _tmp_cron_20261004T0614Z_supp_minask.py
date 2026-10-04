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

    results = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # Correct best-ask: asks are DESC-sorted, so min() is the true best ask
            yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
            no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
            yp = float(yes_ask["price"])
            np_ = float(no_ask["price"])
            results.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    results.sort()
    print(f"Markets with both-side asks: {len(results)}")
    print("True floor (min-ask best sum, top 10):")
    for total, q, yp, np_, liq in results[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    under = [r for r in results if r[0] <= 1.005]
    print(f"Near-miss count (<=1.005, min-ask): {len(under)}")
    for total, q, yp, np_, liq in under:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    c1010 = [r for r in results if r[0] <= 1.010]
    print(f"Count <=1.010: {len(c1010)}")

asyncio.run(scan())
