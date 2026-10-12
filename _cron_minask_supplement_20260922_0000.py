# Supplement: near-miss floor computed with min() best asks (asks are DESC-sorted
# in the CLOB payload, so asks[0] is the WORST ask). Matches detector.py logic.
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

    sums = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            priced += 1
            sums.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    sums.sort()
    return markets and len(markets), priced, sums, scan_time

n, priced, sums, st = asyncio.run(scan())
print(f"[supplement min-ask] {n} markets ({priced} with two-sided asks) in {st:.1f}s")
print(f"[supplement] floor sums (best 8):")
for total, q, yp, np_, liq in sums[:8]:
    tag = " <1.005 NEAR" if total <= 1.005 else (" <1.00 BRACKET" if total < 1.0 else "")
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:,.0f} | {q}{tag}")
brk = [s for s in sums if s[0] < 1.0]
nm = [s for s in sums if 1.0 <= s[0] <= 1.005]
print(f"[supplement] count sum<1.00: {len(brk)} | count 1.00<sum<=1.005: {len(nm)}")
