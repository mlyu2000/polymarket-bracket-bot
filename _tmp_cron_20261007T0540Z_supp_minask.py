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

    true_near = []
    detected = 0
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detected += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            true_near.append((total, m.question[:60], yp, np_, m.liquidity, m.volume_24h if hasattr(m, 'volume_24h') else None))

    true_near.sort()
    print(f"SUPP best-ask scan: {len(markets)} markets ({priced} priced, {detected} detector brackets) in {scan_time:.1f}s")
    print(f"True floor (best-ask Yes+No): {true_near[0][0]:.4f} | {true_near[0][1]}" if true_near else 'no priced markets')
    print("Top 10 best-ask totals <=1.005:")
    for t, q, yp, np_, liq, vol in true_near:
        if t <= 1.005:
            print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("Next 5 above 1.005:")
    above = [x for x in true_near if x[0] > 1.005][:5]
    for t, q, yp, np_, liq, vol in above:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
