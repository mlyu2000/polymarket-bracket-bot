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
    min_total = 9.0
    near_misses = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            min_total = min(min_total, total)
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    brackets.sort()
    return dict(markets=len(markets), priced=priced, min_total=min_total,
                near=near_misses, brackets=brackets, scan_time=scan_time)

r = asyncio.run(scan())
print(f"[best-ask supplement] {r['markets']} markets ({r['priced']} priced) in {r['scan_time']:.1f}s")
print(f"True floor (min Yes+No best asks): {r['min_total']:.4f}")
print(f"BRACKETS (min-ask sum < 1.00): {len(r['brackets'])}")
for s, e, sh, q, liq in r['brackets'][:10]:
    print(f"  🔴 sum={s:.4f} edge={e:.4f} shares={sh} liq={liq} | {q}")
print(f"Near-misses (min-ask sum <= 1.005): {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
