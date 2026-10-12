# Supplement: same scan, but near-miss floor uses BEST ask = min(asks) like
# detector.py (asks[0] is the WORST ask ~0.999 due to DESC ordering).
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

    opps = 0
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total <= 1.01:
                floors.append((total, m.question[:55], yp, np, m.liquidity))

    floors.sort()
    return markets, opps, floors, scan_time

markets, opps, floors, scan_time = asyncio.run(scan())
print(f"Supplement (best-ask floor, {len(markets)} markets, {scan_time:.1f}s)")
print(f"detector.brackets={opps} | markets with best-ask sum<=1.01: {len(floors)}")
for total, q, yp, np, liq in floors[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if floors:
    print(f"TRUE FLOOR = {floors[0][0]:.3f}")
