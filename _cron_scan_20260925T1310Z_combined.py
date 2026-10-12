# Cron run 2026-09-25: provided script verbatim + best-ask supplement (asks[0] is DESC/worst-ask, always 0 near-misses).
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
    # supplement state
    priced = 0
    near_best = []
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

        # supplement: best (min) asks, matching detector.py logic
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yb = min(float(a['price']) for a in yes_book.asks)
            nb = min(float(a['price']) for a in no_book.asks)
            tot = yb + nb
            priced += 1
            if tot <= 1.005:
                near_best.append([round(tot, 4), m.question[:50], yb, nb, m.liquidity])

    near_misses.sort()
    near_best.sort()
    opps.sort(key=lambda o: o['sum'])
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'supp': {'priced': priced, 'near_best': near_best,
                 'floor': (near_best[0][0] if near_best else None)},
    }

result = asyncio.run(scan())
ts = '20260925T1310Z'
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump({'ts': ts,
               'markets': result['markets'],
               'scan_time_s': round(result['scan_time'], 1),
               'brackets': result['opps'],
               'near_misses_asks0': result['near_misses'],
               'priced': result['supp']['priced'],
               'best_floor': result['supp']['floor'],
               'near_misses_bestask': result['supp']['near_best']}, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps({'ts': ts,
                        'markets': result['markets'],
                        'scan_time_s': round(result['scan_time'], 1),
                        'brackets': len(result['opps']),
                        'priced': result['supp']['priced'],
                        'best_floor': result['supp']['floor'],
                        'near_le_1.005_bestask': len(result['supp']['near_best'])}) + '\n')

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"— supplement (best-ask, matches detector.py): priced={result['supp']['priced']} floor={result['supp']['floor']} near<=1.005={len(result['supp']['near_best'])}")
for row in result['supp']['near_best'][:8]:
    print(f"  {row[0]:.3f} | Yes@{row[2]:.3f} No@{row[3]:.3f} | {row[1]}")
