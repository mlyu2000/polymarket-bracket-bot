# Supplement: near-miss block corrected to use BEST ask (min price) instead of
# asks[0] (CLOB asks are DESC-sorted, so asks[0] is the WORST ~0.999 ask).
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    priced = 0
    below_1 = []
    near = []
    floor = 2.0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        if not (0 < yp < 1 and 0 < np_ < 1):
            continue
        priced += 1
        total = yp + np_
        floor = min(floor, total)
        if total < 1.0:
            below_1.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], yp, np_, m.liquidity))

    below_1.sort(); near.sort()
    print(f"[supp min-ask] {priced}/{len(markets)} priced markets in {scan_time:.1f}s; sum<1.00: {len(below_1)}; 1.00<sum<=1.005: {len(near)}; floor={floor:.4f}")
    for total, q, yp, np_, liq in below_1[:10]:
        print(f"  SUB-1 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  NEAR  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
