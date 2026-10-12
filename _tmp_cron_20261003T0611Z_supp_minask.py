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
    scan_time = time.time() - t0

    best = []
    hits = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # CLOB /book asks are DESC-sorted: best ask = min price
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if total < 1.0:
            hits.append((total, m.question[:60], yp, np_, m.liquidity))
        best.append((total, m.question[:60], yp, np_, m.liquidity))

    best.sort()
    hits.sort()
    print(f"[min-ask] {len(markets)} markets in {scan_time:.1f}s")
    print(f"[min-ask] TRUE BRACKETS (best-ask sum < 1.0): {len(hits)}")
    for total, q, yp, np_, liq in hits[:10]:
        print(f"  [HIT] {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"[min-ask] top closest sums (best-ask):")
    for total, q, yp, np_, liq in best[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    nm = [b for b in best if b[0] <= 1.005]
    print(f"[min-ask] near-misses (best-ask <= 1.005): {len(nm)}")

asyncio.run(scan())
