import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    near = []
    priced = 0
    tot_list = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        tot_list.append(total)
        if 1.00 < total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    tot_list.sort()
    print(f"[min-ask supplement] {priced} priced markets in {dt:.1f}s")
    print(f"floor sum: {tot_list[0]:.4f}  p1: {tot_list[1]:.4f}  p2: {tot_list[2]:.4f}  p5: {tot_list[min(4,len(tot_list)-1)]:.4f}")
    print(f"near-misses (1.00 < min-ask sum <= 1.005): {len(near)}")
    for total, q, yp, np_, liq in near[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
