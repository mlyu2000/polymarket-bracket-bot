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

    opps = []
    near = []
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            sums.append(total)
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))

    near.sort()
    sums.sort()
    return len(markets), len(opps), near, sums, scan_time

n, nopps, near, sums, st = asyncio.run(scan())
print(f"markets={n} scan_time={st:.1f}s")
print(f"detector_brackets={nopps}")
print(f"min-ask floor={sums[0]:.4f}  p1={sums[1]:.4f}  p5={sums[4]:.4f}  median={sums[len(sums)//2]:.4f}")
print(f"min-ask near-misses (<=1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
