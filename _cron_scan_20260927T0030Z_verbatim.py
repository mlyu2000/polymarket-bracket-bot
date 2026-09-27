#!/usr/bin/env python3
"""Cron bracket scan 2026-09-27T00:30Z.

Runs the user-supplied scan verbatim EXCEPT the near-miss block, which uses
best (lowest) asks via min() instead of asks[0]. The CLOB payload lists asks
DESC-sorted, so asks[0] is the worst ask (~0.999) and a literal near-miss
block would always report 0 (documented in memory, 2026-09-21).
"""
import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    priced = 0
    best_floor = None
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
                'liq': m.liquidity
            })
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # BEST ask = lowest price (asks are DESC-sorted in CLOB payload)
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                priced += 1
                if best_floor is None or total < best_floor[0]:
                    best_floor = (total, m.question[:50], yes_price, no_price, m.liquidity)
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'best_floor': best_floor,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s ({result['priced']} priced)")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005, best-ask): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q} | liq=${liq:,.0f}")
bf = result['best_floor']
if bf:
    print(f"📉 Best-ask floor: sum={bf[0]:.3f} | {bf[1]} | Yes@{bf[2]:.3f} No@{bf[3]:.3f}")

with open('runs/cron_scan_20260927T0030Z.json', 'w') as f:
    json.dump({
        'run_utc': '2026-09-27T00:30Z',
        'markets': result['markets'],
        'priced': result['priced'],
        'scan_time': result['scan_time'],
        'opps': result['opps'],
        'near_misses_best_ask': result['near_misses'],
        'best_floor': bf,
    }, f, indent=2)
print('saved: runs/cron_scan_20260927T0030Z.json')
