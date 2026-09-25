# Cron scan 2026-09-25T06:55Z — provided script logic, near-misses fixed to use
# BEST asks (min) instead of asks[0] (DESC-sorted worst ask, per known memory note).
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
    priced = 0
    floor = None
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            if floor is None or total < floor[0]:
                floor = (total, m.question[:50])
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    opps.sort(key=lambda o: o['sum'])
    return {
        'ts': '2026-09-25T0655Z',
        'markets': len(markets),
        'priced': priced,
        'best_floor': floor,
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
with open('runs/cron_scan_20260925T0655Z.json', 'w') as f:
    json.dump(result, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(result) + '\n')

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s (priced pairs: {result['priced']})")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']:.0f} | {o['q']}")
print(f"📊 Near-misses (best-ask sum ≤1.005): {len(result['near_misses'])}")
for total, q, yp, npr, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq:.0f} | {q}")
if result['best_floor']:
    print(f"📉 Best-ask floor: {result['best_floor'][0]:.3f} | {result['best_floor'][1]}")
