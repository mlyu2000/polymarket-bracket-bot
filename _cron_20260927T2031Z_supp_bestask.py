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
    best = []
    brackets = 0
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets += 1
            print(f"BRACKET sum={opp.total_cost:.4f} edge={opp.net_edge:.4f} | {m.question[:60]}")
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            best.append((total, m.question[:55], yp, np_, m.liquidity))
    best.sort()
    print(f"SCAN {len(markets)} markets {scan_time:.1f}s priced_books={priced} detector_brackets={brackets}")
    print("TOP10 best-ask sums (min asks):")
    for t, q, yp, np_, liq in best[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"count sum<=1.00: {sum(1 for b in best if b[0] <= 1.00)}")
    print(f"count sum<=1.005: {sum(1 for b in best if b[0] <= 1.005)}")
    print(f"count sum<=1.01: {sum(1 for b in best if b[0] <= 1.01)}")

asyncio.run(scan())
