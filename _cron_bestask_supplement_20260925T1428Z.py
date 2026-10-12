# Combined cron run 2026-09-25T14:28Z: user-provided script (asks[0]) + best-ask (min) supplement.
# detector.py correctly uses min() — CLOB asks are DESC-sorted, so asks[0] = worst ask (~0.999)
# and the provided near-miss block always reports 0.
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
    near_misses = []
    best_near_misses = []
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
            paper.execute(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # provided-script path (asks[0] = worst ask, DESC-sorted)
            yes_p0 = float(yes_book.asks[0]['price'])
            no_p0 = float(no_book.asks[0]['price'])
            t0sum = yes_p0 + no_p0
            if t0sum <= 1.005:
                near_misses.append((t0sum, m.question[:50], yes_p0, no_p0, m.liquidity))
            # corrected path (best ask = min)
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if total <= 1.005:
                best_near_misses.append((round(total, 4), m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    best_near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'scan_time': scan_time,
        'opps': opps,
        'near_misses': near_misses,
        'best_near_misses': best_near_misses,
    }

result = asyncio.run(scan())
r = {
    'ts': '2026-09-25T1428Z',
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'best_floor': (result['best_near_misses'][0] if result['best_near_misses'] else None),
    'near_misses_bestask': result['best_near_misses'],
}
with open('runs/cron_scan_20260925T1428Z.json', 'w') as f:
    json.dump(r, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(r) + '\n')

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq=${o['liq']:,.0f} | {o['q']}")
print(f"📊 Near-misses asks[0] (provided script): {len(result['near_misses'])}")
print(f"📊 Near-misses best-ask ≤1.005 (corrected): {len(result['best_near_misses'])} across {result['priced']} priced markets")
for total, q, yp, np_, liq in result['best_near_misses'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")
