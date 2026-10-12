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
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price,
                         opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if floor is None or total < floor:
                floor = total
            if 1.0 < total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np, m.liquidity))

    near_misses.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps,
            'near_misses': near_misses, 'floor': floor, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"[best-ask audit] markets={result['markets']} priced={result['priced']} floor_sum={result['floor']} in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum<1.00): {len(result['opps'])}")
for total, edge, yp, np, sh, q, liq in sorted(result['opps']):
    print(f"  {total:.4f} edge={edge:.4f} Yes@{yp:.3f} No@{np:.3f} shares={sh} liq={liq} | {q}")
print(f"NEAR-MISSES (1.00<sum<=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
