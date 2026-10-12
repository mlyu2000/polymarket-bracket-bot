# Cron run 2026-09-25. Part A = user-provided script verbatim (asks[0] near-misses are
# known-broken: CLOB asks are DESC-sorted so asks[0]=worst ~0.999 -> always 0).
# Part B = best-ask (min) floor supplement per standing methodology.
import asyncio, json, logging, time
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
    near_misses = []      # provided method: asks[0] (broken, kept for parity)
    bestask_rows = []     # supplement: min-ask sums
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
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                y = min(float(a['price']) for a in yes_book.asks)
                n = min(float(a['price']) for a in no_book.asks)
                bestask_rows.append((y + n, y, n, m.question[:55], m.liquidity))

    near_misses.sort()
    bestask_rows.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': len(bestask_rows),
        'floor': bestask_rows[0][0] if bestask_rows else None,
        'best_near': bestask_rows[:5],
        'best_le1005': [r for r in bestask_rows if r[0] <= 1.005],
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005, provided asks[0] — known-broken): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"--- supplement (best-ask / min) ---")
print(f"priced markets: {result['priced']} | floor (min sum): {result['floor']:.4f}" if result['floor'] else "no priced markets")
print(f"best-ask ≤1.005: {len(result['best_le1005'])}")
for s, y, n, q, liq in result['best_near']:
    print(f"  {s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

import sys
out = {
    'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'markets': result['markets'],
    'priced': result['priced'],
    'brackets': result['opps'],
    'floor_best_ask': result['floor'],
    'near_miss_asks0': len(result['near_misses']),
    'near_miss_bestask': len(result['best_le1005']),
    'best5': result['best_near'],
    'scan_time_s': result['scan_time'],
}
with open(sys.argv[1], 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"persisted -> {sys.argv[1]}")
