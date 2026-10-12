# Supplemental: correct near-miss floor using min(asks) (best ask), since
# Polymarket /book asks are DESC-sorted and asks[0] is the WORST ask (~0.999).
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

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_best = min(float(a['price']) for a in yes_book.asks)
            no_best = min(float(a['price']) for a in no_book.asks)
            total = yes_best + no_best
            rows.append((total, m.question[:60], yes_best, no_best, m.liquidity))
    rows.sort()
    return rows, scan_time, len(markets)

rows, scan_time, n = asyncio.run(scan())
lt1 = [r for r in rows if r[0] < 1.0]
nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"min(asks) variant: {n} markets in {scan_time:.1f}s ({len(rows)} priced)")
print(f"true brackets sum<1.00: {len(lt1)}")
for total, q, yp, np_, liq in lt1:
    print(f"  [LT1] {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"near-misses 1.000-1.005: {len(nm)}")
for total, q, yp, np_, liq in nm[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("lowest 5 overall:")
for total, q, yp, np_, liq in rows[:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
