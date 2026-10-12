import asyncio, logging, time, json
from datetime import datetime, timezone
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
    near_misses = []      # provided method: asks[0] (known to under-report, asks DESC-sorted)
    minask_near = []      # corrected floor: min ask per side
    best = None
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
                ymin = min(float(a['price']) for a in yes_book.asks)
                nmin = min(float(a['price']) for a in no_book.asks)
                tmin = ymin + nmin
                priced += 1
                if best is None or tmin < best[0]:
                    best = (tmin, m.question[:60], ymin, nmin, m.liquidity)
                if tmin <= 1.005:
                    minask_near.append((tmin, m.question[:50], ymin, nmin, m.liquidity))

    near_misses.sort()
    minask_near.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'minask_near': minask_near,
        'best': best,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
print(f"[{ts}]")
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s ({result['priced']} with two-sided asks)")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"📊 Near-misses (≤1.005, provided asks[0] method): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📉 Corrected best Yes+No min-ask floor: {result['best'][0]:.4f}" if result['best'] else "📉 No priced markets")
if result['best']:
    t, q, yp, np, liq = result['best']
    print(f"   → {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"📊 Corrected near-misses (min-ask ≤1.005): {len(result['minask_near'])}")
for total, q, yp, np, liq in result['minask_near'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

out = {
    'ts': ts,
    'method': 'provided(asks[0]) + detector + minask floor',
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time': result['scan_time'],
    'best_min_sum': result['best'][0] if result['best'] else None,
    'best_min_sum_market': result['best'][1] if result['best'] else None,
    'brackets': result['opps'],
    'near_le_1005_provided_asks0': [list(x) for x in result['near_misses']],
    'near_le_1005_minask': [list(x) for x in result['minask_near']],
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(out) + '\n')
print("📁 persisted to results/cron_scan_history.jsonl")
