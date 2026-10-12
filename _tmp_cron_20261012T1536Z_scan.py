"""Cron bracket scan (20261012T1536Z).

NOTE: the verbatim prompt script uses `asks[0]` for the near-miss block. Polymarket
CLOB /book lists asks DESC-sorted, so asks[0] is the WORST ask (~0.999) and that
block always reports 0 near-misses (known artifact). Brackets come from
BracketDetector.detect(), which correctly uses min(asks). This run fixes ONLY the
near-miss block to use the true best ask = min(all asks), matching the detector.
"""
import asyncio
import logging
import time

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
            paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                # True best ask = min over the ladder (asks are DESC-sorted).
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }


result = asyncio.run(scan())
print(f"SCAN: {result['markets']} markets, {result['priced']} two-sided priced, in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum<1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  BRACKET {o['sum']:.4f} (net_edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']:.0f} | {o['q']}")
print(f"NEAR_MISSES (1.000<sum<=1.005, min-ask): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
