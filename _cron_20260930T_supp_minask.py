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
    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], opp.yes_price, opp.no_price))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya+na, m.question[:50], ya, na, m.liquidity))
    rows.sort()
    return scan_time, brackets, rows

scan_time, brackets, rows = asyncio.run(scan())
print(f"min-ask supplemental scan: {len(rows)} priced markets in {scan_time:.1f}s")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for s,e,sh,q,yp,np in sorted(brackets):
    print(f"  {s:.3f} edge={e:.4f} shares={sh} Yes@{yp:.3f} No@{np:.3f} | {q}")
print("lowest 10 min-ask totals:")
for total,q,yp,na,liq in rows[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{na:.3f} | liq={liq} | {q}")
