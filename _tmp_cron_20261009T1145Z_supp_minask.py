"""Supplementary near-miss pass using BEST (min-price) asks, consistent with
detector.py. The verbatim cron block uses asks[0], which on the CLOB payload
is the WORST ask (asks are DESC-sorted), so near-misses there are always 0.
"""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        priced += 1
        total = yp + np_
        rows.append((total, m.question[:60], yp, np_, m.liquidity, m.active, m.closed))
    rows.sort()
    return len(markets), priced, rows

markets_n, priced_n, rows = asyncio.run(scan())
print(f"Markets: {markets_n} | priced pairs: {priced_n}")
print("--- Best 10 (lowest sum) ---")
for total, q, yp, np_, liq, active, closed in rows[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:,.0f} | {q}")
print("--- Floor stats ---")
if rows:
    import statistics
    sums = [r[0] for r in rows]
    print(f"  min={min(sums):.4f} median={statistics.median(sums):.4f} max={max(sums):.4f}")
    lt1005 = [s for s in sums if s <= 1.005]
    lt1000 = [s for s in sums if s < 1.000]
    print(f"  count<=1.005: {len(lt1005)} | count<1.000: {len(lt1000)}")
