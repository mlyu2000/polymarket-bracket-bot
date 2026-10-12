import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best_sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            best_sums.append((yp + np, m.question[:50], yp, np, m.liquidity))

    best_sums.sort()
    print(f"priced markets: {len(best_sums)} / {len(markets)}")
    print("floor (best-ask min sum): %.3f" % best_sums[0][0] if best_sums else "no priced markets")
    print("Near-misses (best-ask <=1.005): %d" % sum(1 for s in best_sums if s[0] <= 1.005))
    for total, q, yp, np, liq in best_sums[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
