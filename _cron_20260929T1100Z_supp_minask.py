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

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    detector_opps = [o for m, (yb, nb) in zip(markets, all_books) if (o := detector.detect(m, yb, nb))]
    return len(markets), scan_time, rows, detector_opps

n, t, rows, dopps = asyncio.run(scan())
print(f"Markets: {n} in {t:.1f}s | detector PASS count: {len(dopps)}")
print("True floor (best asks, sum = yes_ask_min + no_ask_min):")
for s, q, yp, np, liq in rows[:10]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
below1 = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if r[0] <= 1.005]
print(f"sum<1.00: {len(below1)} | sum<=1.005: {len(near)}")
