import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

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
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            near.append((ya + na, m.question[:50], ya, na, m.liquidity))
    near.sort()
    return markets, opps, near, scan_time

markets, opps, near, scan_time = asyncio.run(scan())
print(f"MIN-ASK SUPPLEMENT 2026-09-27T07:42Z: {len(markets)} markets in {scan_time:.1f}s")
print(f"BRACKETS (best-ask sum < 1.00): {len([1 for t,*_ in near if t < 1.0])}")
print(f"Best 8 sums (min-ask):")
for total, q, yp, np, liq in near[:8]:
    flag = " <<BRACKET" if total < 1.0 else ""
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}{flag}")
