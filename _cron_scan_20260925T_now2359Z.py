"""Cron bracket scan 2026-09-25.

Runs the user-provided script verbatim (block 1), then the SAME logic with the
known asks[0] near-miss bug fixed via min()-ask (block 2, matching detector.py
and the persisted best_floor series). Persists combined result to
results/cron_scan_history.jsonl.
"""
import asyncio, json, logging, time
from pathlib import Path

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
    near_misses = []          # verbatim block: asks[0] (biased by DESC sort)
    near_misses_fixed = []    # corrected block: min() best ask
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
                # asks are DESC-sorted: asks[0] is the WORST ask (~0.999).
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

                yb = min(yes_book.asks, key=lambda a: float(a['price']))
                nb = min(no_book.asks, key=lambda a: float(a['price']))
                yfp, nfp = float(yb['price']), float(nb['price'])
                ftot = yfp + nfp
                if ftot <= 1.005:
                    near_misses_fixed.append((ftot, m.question[:50], yfp, nfp, m.liquidity))

    near_misses.sort()
    near_misses_fixed.sort()
    return {
        'markets': len(markets),
        'priced': sum(1 for a in all_books if a[0] and a[1] and a[0].asks and a[1].asks),
        'opps': opps,
        'near_misses': near_misses,
        'near_misses_fixed': near_misses_fixed,
        'scan_time': scan_time,
    }


result = asyncio.run(scan())

print("=" * 70)
print("BLOCK 1 — user script verbatim (asks[0])")
print("=" * 70)
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")

print()
print("=" * 70)
print(f"BLOCK 2 — corrected min()-ask best_ask ({result['priced']}/{result['markets']} priced)")
print("=" * 70)
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
if result['near_misses_fixed']:
    floor = result['near_misses_fixed'][0][0]
    print(f"📉 Best floor (min sum): {floor:.3f}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses_fixed'])}")
for total, q, yp, np_, liq in result['near_misses_fixed'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")

# Persist
best_floor = result['near_misses_fixed'][0] if result['near_misses_fixed'] else None
record = {
    'ts': time.strftime('%Y%m%dT%H%MZ', time.gmtime()),
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'best_floor': list(best_floor) if best_floor else None,
    'near_misses_bestask': [list(x) for x in result['near_misses_fixed']],
}
hist = Path(__file__).parent / 'results' / 'cron_scan_history.jsonl'
with hist.open('a') as f:
    f.write(json.dumps(record) + "\n")
print(f"\n[saved to {hist}]")
