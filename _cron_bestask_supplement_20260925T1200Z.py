"""Supplement: near-misses computed with BEST asks (min price), not asks[0].
CLOB API lists asks DESC-sorted, so asks[0] is the worst ask — the verbatim
cron block under-reports. This mirrors the detector's min() logic."""
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
    return markets, near, priced, scan_time

markets, near, priced, scan_time = asyncio.run(scan())
print(f"[supplement · best asks] {priced} priced markets of {len(markets)} in {scan_time:.1f}s")
print(f"Near-misses (best-ask sum <= 1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")
if near:
    print(f"True floor this run: {near[0][0]:.4f}")
else:
    print("No sums <= 1.005 found at best asks.")
