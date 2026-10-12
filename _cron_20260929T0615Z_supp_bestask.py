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

    sums = []
    detector_opps = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detector_opps += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    sums.sort()
    return markets, sums, detector_opps, scan_time

markets, sums, detector_opps, scan_time = asyncio.run(scan())
priced = len(sums)
print(f"🔍 Best-ask recheck: {len(markets)} markets, {priced} with both asks, in {scan_time:.1f}s")
print(f"✅ Detector-brackets (net edge >= {0.01}): {detector_opps}")
print(f"Sum<1.00 (best asks): {sum(1 for s in sums if s[0] < 1.0)}")
print(f"Sum<=1.005 (best asks): {sum(1 for s in sums if s[0] <= 1.005)}")
print(f"Sum<=1.01 (best asks): {sum(1 for s in sums if s[0] <= 1.01)}")
print("Top-10 lowest best-ask sums:")
for total, q, yp, np_, liq in sums[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
