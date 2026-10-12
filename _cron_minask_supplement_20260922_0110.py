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

    opps, near_misses = [], []
    priced = 0
    floor = (9.9, None)
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        elif yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            npr = min(float(a['price']) for a in no_book.asks)
            total = yp + npr
            priced += 1
            if total < floor[0]:
                floor = (total, m.question[:60])
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yp, npr, m.liquidity))
    near_misses.sort()
    print(f"[min-ask supplement] {len(markets)} markets, {priced} with both books, in {scan_time:.1f}s")
    print(f"Floor (min-ask sum): {floor[0]:.4f} | {floor[1]}")
    print(f"Near-misses (sum<=1.005, min-ask): {len(near_misses)}")
    for t, q, yp, npr, liq in near_misses[:5]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")

asyncio.run(scan())
