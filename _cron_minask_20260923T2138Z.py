# Reconciled supplement: near-miss block with best-ask = min(price) (asks are DESC-sorted).
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

    brackets = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if total <= 1.005:
                near_misses.append((round(total, 4), m.question[:50], yes_price, no_price, m.liquidity))

    brackets.sort()
    near_misses.sort()
    return markets, brackets, near_misses, scan_time

markets, brackets, near_misses, scan_time = asyncio.run(scan())
print(f"[supplement] {len(markets)} markets in {scan_time:.1f}s")
print(f"[supplement] detector brackets (raw sum<1.005 view incl. sub-margin): {len(brackets)}")
for s, e, sh, q in brackets[:10]:
    print(f"  🔴 sum={s:.4f} net_edge={e:.4f} shares={sh} | {q}")
print(f"[supplement] best-ask near-misses (sum<=1.005): {len(near_misses)}")
for total, q, yp, np_, liq in near_misses[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
