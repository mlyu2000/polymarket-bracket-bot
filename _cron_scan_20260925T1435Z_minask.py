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
    # Supplement: best-ask (min) methodology — asks lists are DESC-sorted,
    # so asks[0] is NOT the best ask. detector.py already uses min().
    best_near = []
    floor = None
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
                # best-ask supplement
                by = min(float(a['price']) for a in yes_book.asks)
                bn = min(float(a['price']) for a in no_book.asks)
                bt = by + bn
                priced += 1
                if floor is None or bt < floor:
                    floor = bt
                if bt <= 1.005:
                    best_near.append((bt, m.question[:50], by, bn, m.liquidity))

    near_misses.sort()
    best_near.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'best_near': best_near,
        'floor': floor,
        'priced': priced,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📊 SUPPLEMENT best-ask methodology: priced={result['priced']} floor={result['floor']:.3f} near<=1.005={len(result['best_near'])}")
for total, q, yp, np, liq in result['best_near'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

import json, datetime
ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%MZ')
out = {
    'ts': ts,
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'best_floor': list(result['best_near'][0]) if result['best_near'] else None,
    'near_misses_bestask': [list(x) for x in result['best_near']],
}
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump(out, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(out) + '\n')
print(f"PERSISTED runs/cron_scan_{ts}.json")
