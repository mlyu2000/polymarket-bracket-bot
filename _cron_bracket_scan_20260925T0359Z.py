# Cron run 2026-09-25T0359Z.
# Part 1: user-provided script VERBATIM (near-misses use asks[0]).
# Part 2: supplement with BEST-ask (min) near-misses, matching detector.py logic.
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
    best_misses = []
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            tot = yp + np_
            priced += 1
            if tot <= 1.005:
                best_misses.append([round(tot, 4), m.question[:50], yp, np_, m.liquidity])

    near_misses.sort()
    best_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': priced,
        'best_misses': best_misses,
    }

result = asyncio.run(scan())
ts = '20260925T0359Z'
record = {
    'ts': ts,
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'best_floor': (result['best_misses'][0] if result['best_misses'] else None),
    'near_misses_bestask': result['best_misses'],
    'near_misses_asks0': [list(x) for x in result['near_misses']],
}
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump(record, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(record) + '\n')

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005, asks[0] verbatim): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"--- supplement: best-ask (min) near-misses, {result['priced']} priced books ---")
print(f"📊 Near-misses (≤1.005, best ask): {len(result['best_misses'])}")
for total, q, yp, np_, liq in result['best_misses'][:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if result['best_misses']:
    print(f"Floor (best-ask): {result['best_misses'][0][0]}")
else:
    print("Floor (best-ask): none <= 1.005")
