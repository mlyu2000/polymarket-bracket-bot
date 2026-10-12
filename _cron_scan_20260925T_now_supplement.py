"""Cron scan 2026-09-25 (latest run): user-specified asks[0] scan + best-ask floor supplement (1 fetch)."""
import asyncio, logging, time
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
    # best-ask supplement state
    best_sum = None
    best_q = None
    best_parts = None
    priced = 0
    best_near = []

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
                # best-ask floor measurement
                by = min(float(a['price']) for a in yes_book.asks)
                bn = min(float(a['price']) for a in no_book.asks)
                bs = by + bn
                if bs > 0:
                    priced += 1
                    if best_sum is None or bs < best_sum:
                        best_sum, best_q, best_parts = bs, m.question[:60], (by, bn)
                    if bs <= 1.005:
                        best_near.append((bs, m.question[:50], by, bn, m.liquidity))

    near_misses.sort()
    best_near.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'best_sum': best_sum,
        'best_q': best_q,
        'best_parts': best_parts,
        'priced': priced,
        'best_near': best_near,
    }

result = asyncio.run(scan())
import json
from datetime import datetime, timezone
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
dump = {
    'ts': ts,
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'near_misses_asks0': result['near_misses'],
    'best_floor': [result['best_sum'], result['best_q'], result['best_parts'][0], result['best_parts'][1]],
    'near_misses_bestask': result['best_near'],
}
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump(dump, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(dump) + '\n')
print(f"💾 persisted runs/cron_scan_{ts}.json")
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📐 best-ask floor: sum={result['best_sum']:.3f} | Yes@{result['best_parts'][0]:.3f} No@{result['best_parts'][1]:.3f} | {result['best_q']} | priced={result['priced']} | best-ask near-misses(<=1.005)={len(result['best_near'])}")
for t, q, yp, np, liq in result['best_near'][:5]:
    print(f"  B {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
