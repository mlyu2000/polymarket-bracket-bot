"""Cron run 2026-09-23T08:50Z.

Part A: user-provided scan script verbatim (asks[0] near-misses + paper exec).
Part B: mechanism-agnostic min-ask floor supplement over the SAME books
        (asks[0] on the CLOB is the WORST ask — descending sort — so the
        provided near-miss block under-reports; detector.py uses min() and
        is correct).
"""
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
    near_misses = []          # provided method: asks[0]
    minask_near = []          # supplement: min-price ask
    priced = 0
    best_min_sum = None

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

        # Supplement: mechanism-agnostic min-ask sum for every priced market
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            ym = min(float(a['price']) for a in yes_book.asks)
            nm = min(float(a['price']) for a in no_book.asks)
            s = round(ym + nm, 4)
            if best_min_sum is None or s < best_min_sum[0]:
                best_min_sum = (s, m.question[:50], ym, nm, m.liquidity)
            if s <= 1.005:
                minask_near.append((s, m.question[:50], ym, nm, m.liquidity))

    near_misses.sort()
    minask_near.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': priced,
        'best_min_sum': best_min_sum,
        'minask_near': minask_near,
        'paper_stats': paper.stats,
    }


result = asyncio.run(scan())

out = {
    'ts': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()),
    'method': 'provided(asks[0]) + detector + minask floor',
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_seconds': round(result['scan_time'], 2),
    'best_min_sum': result['best_min_sum'][0] if result['best_min_sum'] else None,
    'best_min_sum_market': result['best_min_sum'][1] if result['best_min_sum'] else None,
    'brackets': result['opps'],
    'near_le_1005_provided_asks0': [
        {'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l} for t, q, y, n, l in result['near_misses']
    ],
    'near_le_1005_minask': [
        {'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l} for t, q, y, n, l in result['minask_near']
    ],
    'paper_stats': result['paper_stats'],
}
import os
os.makedirs('runs', exist_ok=True)
path = f"runs/cron_scan_{out['ts']}.json"
with open(path, 'w') as f:
    json.dump(out, f, indent=1)

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005, provided asks[0]): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📐 Floor supplement: priced={result['priced']} best_min_sum={out['best_min_sum']}")
print(f"   near<=1.005 (minask): {len(result['minask_near'])}")
for t, q, y, n, l in result['minask_near'][:8]:
    print(f"  {t:.3f} | Yes@{y:.3f} No@{n:.3f} | liq=${l:,.0f} | {q}")
print(f"💾 saved {path}")
