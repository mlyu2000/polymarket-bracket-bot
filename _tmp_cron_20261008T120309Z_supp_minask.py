import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # min-ask (true best ask; asks[0] is DESC-sorted worst ask)
            yes_ask = min(float(a['price']) for a in yes_book.asks)
            no_ask = min(float(a['price']) for a in no_book.asks)
            total = yes_ask + no_ask
            totals.append((total, m.question[:60], yes_ask, no_ask, m.liquidity))

    totals.sort()
    brackets = [t for t in totals if t[0] < 1.0]
    near = [t for t in totals if 1.0 <= t[0] <= 1.005]
    print(f"supp-scan: {len(markets)} markets in {scan_time:.1f}s (best-ask/min based)")
    print(f"true brackets (sum<1.00): {len(brackets)}")
    for t in brackets[:10]:
        print(f"  {t[0]:.4f} | Yes@{t[2]:.3f} No@{t[3]:.3f} | liq={t[4]} | {t[1]}")
    print(f"near-misses (1.00-1.005): {len(near)}")
    for t in near[:5]:
        print(f"  {t[0]:.4f} | Yes@{t[2]:.3f} No@{t[3]:.3f} | liq={t[4]} | {t[1]}")
    if totals:
        print(f"floor (min sum): {totals[0][0]:.4f} {totals[0][1]}")

asyncio.run(scan())
