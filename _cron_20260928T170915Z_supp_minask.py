import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    sums.sort()
    print(f"supp: {len(markets)} markets, {len(sums)} priced pairs in {time.time()-t0:.1f}s")
    print("BEST-ASK (min) floor, top 10:")
    for total, q, yp, np_, liq in sums[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    below1 = [s for s in sums if s[0] < 1.0]
    print(f"pairs with min-ask sum < 1.00: {len(below1)}")
    for total, q, yp, np_, liq in below1[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    nm = [s for s in sums if s[0] <= 1.005]
    print(f"true near-misses (<=1.005): {len(nm)}")

asyncio.run(supp())
