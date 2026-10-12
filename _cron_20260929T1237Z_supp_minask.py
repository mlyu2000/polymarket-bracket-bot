# Supplementary: near-miss floor using BEST asks (min price), since CLOB
# asks are DESC-sorted and asks[0] is the worst level (known issue, 2026-09-21 memo).
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

    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    near_misses.sort()
    return markets, near_misses, priced, scan_time

markets, near_misses, priced, scan_time = asyncio.run(scan())
print(f"[supp min-ask] {len(markets)} markets ({priced} priced) in {scan_time:.1f}s")
print(f"[supp min-ask] Near-misses (sum<=1.005): {len(near_misses)}")
for total, q, yp, np, liq in near_misses[:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
