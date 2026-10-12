# Supplementary: same scan but near-misses computed with min(best-ask) per side,
# because asks[] is DESC-sorted in the CLOB payload (asks[0] is the WORST ask).
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

    opps = []
    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((m, opp))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return markets, opps, near_misses, priced, scan_time

markets, opps, near_misses, priced, scan_time = asyncio.run(scan())
print(f"MIN-ASK SUPP SCAN: {len(markets)} markets ({priced} priced) in {scan_time:.1f}s")
print(f"BRACKETS via detector (min-ask): {len(opps)}")
for m, o in opps:
    print(f"  sum={o.total_cost:.4f} edge={o.net_edge:.4f} | Yes@{o.yes_price:.3f} No@{o.no_price:.3f} | shares={o.max_shares} | {m.question[:60]}")
print(f"Near-misses <=1.005 (min-ask): {len(near_misses)}")
for total, q, yp, np, liq in near_misses[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
