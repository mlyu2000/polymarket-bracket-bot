"""Supplementary near-miss pass: best ask = min(price) across asks.

The verbatim cron script's near-miss block uses asks[0], but the CLOB
payload lists asks in DESCENDING price order, so asks[0] is the WORST ask
(~0.999) and near-miss totals always exceed 1.005 -> always 0.
detector.py already uses min(); this mirrors detector's mechanism using
only OrderBook public fields so no class internals are hardcoded.
"""
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
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            if total <= 1.005:
                near.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    near.sort()
    return markets, near, scan_time, priced

markets, near, scan_time, priced = asyncio.run(scan())
print(f"[supp min-ask] {len(markets)} markets ({priced} with both-sided books) in {scan_time:.1f}s")
print(f"[supp min-ask] Near-misses best-ask sum<=1.005: {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
