import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not getattr(book, 'asks', None):
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    priced = 0
    opps = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        ya = best_ask(yes_book)
        na = best_ask(no_book)
        if ya is not None and na is not None:
            priced += 1
            total = ya + na
            near.append((total, m.question[:60], ya, na, m.liquidity))
    near.sort()
    print(f"best-ask scan: {len(markets)} markets, {priced} priced, {len(opps)} brackets, {scan_time:.1f}s")
    print("TIGHTES 10 (true best-ask sums):")
    for total, q, yp, np, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    lt1 = [n for n in near if n[0] < 1.0]
    print(f"sum<1.0 count: {len(lt1)}")
    for total, q, yp, np, liq in lt1:
        print(f"  SUB-COMPLETION {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
