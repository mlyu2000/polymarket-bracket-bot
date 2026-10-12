import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    sums = []
    brackets_true = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets_true.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np, m.question[:50], yp, np, m.liquidity, m.active, m.closed))

    sums.sort()
    return markets, all_books, sums, brackets_true, scan_time

markets, all_books, sums, brackets_true, scan_time = asyncio.run(scan())
priced = [s for s in sums if 0 < s[0] < 2]
print(f"Supplement (min-ask): {len(markets)} markets in {scan_time:.1f}s; {len(sums)} with both books; {len(priced)} priced")
print(f"True brackets (detector, min-ask, sum<1): {len(brackets_true)}")
for t, e, sh, q, liq in brackets_true:
    print(f"  🔴 sum={t:.3f} edge={e:.4f} shares={sh} liq={liq} | {q}")
print("Floor / top 8 lowest min-ask sums:")
for total, q, yp, np, liq, act, closed in sums[:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"Count sum<=1.005: {sum(1 for s in sums if s[0]<=1.005)} | <=1.01: {sum(1 for s in sums if s[0]<=1.01)} | <=1.02: {sum(1 for s in sums if s[0]<=1.02)}")
