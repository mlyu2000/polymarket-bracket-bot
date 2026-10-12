# Supplementary scan: correct best-ask (min price) near-miss floor.
# CLOB /book asks are DESC-sorted, so asks[0] is the WORST ask; the verbatim
# cron script's near-miss block always sees ~0.999+ sums. This uses min() like
# detector.py does.
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
    el = time.time() - t0

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np, m.question[:50], yp, np, m.liquidity))
    sums.sort()
    print(f"[supp min-ask] {len(sums)} priced markets in {el:.1f}s")
    print("Top 8 closest to bracket (best-ask Yes+No):")
    for s, q, yp, np, liq in sums[:8]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    below1 = [s for s in sums if s[0] < 1.0]
    print(f"Markets with true best-ask sum < 1.00: {len(below1)}")

asyncio.run(scan())
