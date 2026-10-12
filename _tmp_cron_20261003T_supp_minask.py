"""Supplementary near-miss pass with BEST asks (min price).
asks[0] in CLOB /book is the WORST ask (asks are DESC-sorted), so the
cron-provided near-miss block under-reports. detector.py uses min() correctly.
This script recomputes near-misses using min() best asks over the same market set.
"""
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
    floor_sum = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity,
            })
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if floor_sum is None or total < floor_sum:
                floor_sum = total
            if 1.0 < total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np_, m.liquidity))
    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'floor_sum': floor_sum,
        'scan_time': scan_time,
    }

r = asyncio.run(scan())
print(f"bestask scan: {r['markets']} markets ({r['priced']} priced) in {r['scan_time']:.1f}s")
print(f"BRACKETS via detector: {len(r['opps'])}")
for o in r['opps']:
    print(f"  sum={o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
print(f"TRUE FLOOR min(Yes_ask+No_ask) across priced markets: {r['floor_sum']}")
print(f"NEAR-MISSES (best asks, 1.0 < sum <= 1.005): {len(r['near_misses'])}")
for total, q, yp, np_, liq in r['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
