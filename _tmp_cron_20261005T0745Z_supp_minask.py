import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    best = []      # true best-ask sums across all priced markets
    near = []      # best-ask near misses <= 1.005
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        best.append((total, m.question[:60], yp, np_, m.liquidity))
        if total <= 1.005:
            near.append((total, m.question[:60], yp, np_, m.liquidity))

    best.sort()
    near.sort()
    print(f"supp scan {len(markets)} markets {dt:.1f}s; priced={len(best)}")
    if best:
        print(f"TRUE best-ask floor sum: {best[0][0]:.4f} | {best[0][1]} (Yes@{best[0][2]:.3f} No@{best[0][3]:.3f} liq={best[0][4]})")
    print(f"sum<1.00: {sum(1 for b in best if b[0] < 1.0)}")
    print(f"near (<=1.005, best-ask): {len(near)}")
    for total, q, yp, np_, liq in near[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("top-8 lowest overall sums:")
    for total, q, yp, np_, liq in best[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
