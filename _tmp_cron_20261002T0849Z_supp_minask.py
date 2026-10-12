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
    dt = time.time() - t0

    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            totals.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    totals.sort()
    print(f"[supp] {len(totals)} priced markets in {dt:.1f}s (best-ask = min(), corrected)")
    br = [t for t in totals if t[0] < 1.0]
    nm = [t for t in totals if 1.0 <= t[0] <= 1.005]
    print(f"[supp] true brackets (<1.00): {len(br)}")
    for t in br:
        print(f"  🔴 {t[0]:.4f} | Yes@{t[2]:.3f} No@{t[3]:.3f} | liq={t[4]:.0f} | {t[1]}")
    print(f"[supp] near-misses (1.000–1.005): {len(nm)}")
    for t in nm[:10]:
        print(f"  {t[0]:.4f} | Yes@{t[2]:.3f} No@{t[3]:.3f} | liq={t[4]:.0f} | {t[1]}")
    print("[supp] 10 lowest sums overall:")
    for t in totals[:10]:
        print(f"  {t[0]:.4f} | Yes@{t[2]:.3f} No@{t[3]:.3f} | liq={t[4]:.0f} | {t[1]}")

asyncio.run(scan())
