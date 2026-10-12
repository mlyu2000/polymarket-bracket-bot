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

    priced = 0
    sub1 = []
    near = []
    best_floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        if best_floor is None or total < best_floor[0]:
            best_floor = (total, m.question[:60])
        if total < 1.0:
            sub1.append((total, m.question[:60], ya, na, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], ya, na, m.liquidity))
    sub1.sort(); near.sort()
    return dict(markets=len(markets), priced=priced, scan_time=scan_time,
                sub1=sub1, near=near, floor=best_floor)

r = asyncio.run(scan())
print(f"minask scan: {r['markets']} markets, {r['priced']} priced, {r['scan_time']:.1f}s")
print(f"TRUE sum<1.00 (best asks): {len(r['sub1'])}")
for total, q, yp, np_, liq in r['sub1'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"TRUE near-miss 1.00<=sum<=1.005: {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Global best-ask floor: {r['floor'][0]:.4f} | {r['floor'][1]}")
