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

    true_brackets = []
    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            true_brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        elif yes_book and no_book and yes_book.asks and no_book.asks:
            # best ask = min() across levels (asks are DESC-sorted in /book)
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            priced += 1
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np, m.liquidity))

    near_misses.sort()
    true_brackets.sort()
    return dict(markets=len(markets), priced=priced, tb=true_brackets, nm=near_misses, t=scan_time)

r = asyncio.run(scan())
print(f"markets={r['markets']} priced={r['priced']} best-ask scan {r['t']:.1f}s")
print(f"TRUE BRACKETS via detector: {len(r['tb'])}")
for s, e, sh, q, liq in r['tb']:
    print(f"  sum={s:.4f} edge={e:.4f} shares={sh} liq={liq} | {q}")
print(f"NEAR-MISSES (best-ask sum <= 1.005): {len(r['nm'])}")
for total, q, yp, np, liq in r['nm'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
