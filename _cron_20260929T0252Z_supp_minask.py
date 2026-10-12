# Supplement: true best-ask analysis. Polymarket CLOB /book returns asks DESC-sorted,
# so asks[0] is the WORST ask (~0.999). detector.py already uses min() internally;
# this script corrects the near-miss/floor reporting to use min over asks.
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
    priced = 0
    floor = 9.9
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and getattr(yes_book, 'asks', None) and getattr(no_book, 'asks', None):
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            priced += 1
            if total < floor:
                floor = total
            if 1.0 <= total <= 1.005:
                near_misses.append((total, m.question[:50], ya, na, m.liquidity))

    near_misses.sort()
    return dict(markets=len(markets), priced=priced, floor=floor, brackets=sorted(brackets), near=near_misses, t=scan_time)

r = asyncio.run(scan())
print(f"[supp-minask] markets={r['markets']} priced={r['priced']} scan={r['t']:.1f}s true_floor_sum={r['floor']:.3f}")
print(f"[supp-minask] BRACKETS detected: {len(r['brackets'])}")
for total, edge, yp, np_, shares, q, liq in r['brackets']:
    print(f"  🔴 sum={total:.3f} edge={edge:.4f} Yes@{yp:.3f} No@{np_:.3f} shares={shares} liq={liq} | {q}")
print(f"[supp-minask] Near-misses 1.000-1.005 (true best asks): {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
