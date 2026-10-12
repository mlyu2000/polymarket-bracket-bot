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

    detected = []
    corrected_near = []
    floor = None
    floor_q = None
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detected.append((opp.total_cost, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            # CORRECTED: asks are DESC-sorted; best ask = min price
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if floor is None or total < floor:
                floor = total
                floor_q = m.question[:60]
            if total <= 1.005 and not opp:
                corrected_near.append((total, m.question[:50], yp, np_, m.liquidity))

    corrected_near.sort()
    detected.sort()
    print(f"[min-ask corrected] {priced}/{len(markets)} markets priced, scan {scan_time:.1f}s")
    print(f"[floor] min sum(Yes+No best asks) = {floor:.4f} | {floor_q}")
    print(f"[brackets sum<1.00 via corrected min-ask]: {len(detected)}")
    for s, q in detected[:10]:
        print(f"  {s:.4f} | {q}")
    print(f"[near-misses <=1.005 corrected]: {len(corrected_near)}")
    for total, q, yp, np_, liq in corrected_near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
