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
    opps = []
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np, m.liquidity))
    near.sort()
    opps.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps, 'near': near, 't': scan_time}

r = asyncio.run(scan())
print(f"markets={r['markets']} priced={r['priced']} scan={r['t']:.1f}s")
print(f"BRACKETS(best-ask min, sum<1.00): {len(r['opps'])}")
for s, e, yp, np, sh, q, liq in r['opps'][:10]:
    print(f"  sum={s:.4f} edge={e:.4f} | Yes@{yp:.3f} No@{np:.3f} | {sh} shares | liq={liq} | {q}")
print(f"NEAR-MISSES(best-ask min, <=1.005): {len(r['near'])}")
for total, q, yp, np, liq in r['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
