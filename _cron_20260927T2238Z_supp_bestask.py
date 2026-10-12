"""Supplement: near-misses computed with BEST ask (min price) per side,
since the CLOB /book asks list is DESC-sorted (asks[0] = worst)."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from models import OrderBook  # noqa

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

    brackets = 0
    best_sums = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if total <= 1.005:
            best_sums.append((round(total, 4), m.question[:60], ya, na, m.liquidity))
        best_sums.sort()
    floor = None
    return {
        'markets': len(markets),
        'priced': priced,
        'brackets': brackets,
        'near': best_sums,
        'scan_time': time.time() - t0,
    }

r = asyncio.run(scan())
print(f"Supp(best-ask): {r['markets']} markets ({r['priced']} priced) in {r['scan_time']:.1f}s")
print(f"BRACKETS (net_edge>=threshold via detector): {r['brackets']}")
print(f"Near-misses best-ask sum<=1.005: {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
