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

    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    return markets, priced, near, scan_time

markets, priced, near, scan_time = asyncio.run(scan())
print(f"[supp best-ask] {len(markets)} markets ({priced} with both books) in {scan_time:.1f}s")
print(f"[supp] near-misses (min-ask sum <= 1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if near:
    floors = [t for t, *_ in near]
    print(f"[supp] true floor this run: {min(floors):.3f}")
