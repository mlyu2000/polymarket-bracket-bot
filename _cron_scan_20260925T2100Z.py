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
    near_misses = []
    priced = 0
    floor = (9.99, '')
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
                priced += 1
                # asks are DESC-sorted: asks[0] is worst. Use true best asks.
                ybest = min(float(a['price']) for a in yes_book.asks)
                nbest = min(float(a['price']) for a in no_book.asks)
                total = ybest + nbest
                if total < floor[0]:
                    floor = (total, m.question[:50])
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], ybest, nbest, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'floor': floor,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  [BRACKET] {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"Best-ask floor: {result['floor'][0]:.3f} | {result['floor'][1]}")
print(f"Near-misses best-ask (<=1.005): {len(result['near_misses'])}")
for total, q, yp, npx, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npx:.3f} | liq={liq} | {q}")

# Persist
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%MZ')
out = {
    'ts': ts,
    'markets': result['markets'],
    'priced': result['priced'],
    'brackets': result['opps'],
    'floor': result['floor'],
    'near_miss_count': len(result['near_misses']),
    'near_misses': result['near_misses'][:10],
    'scan_time': result['scan_time'],
}
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump(out, f, indent=2)
hist_line = {'ts': ts, 'markets': result['markets'], 'priced': result['priced'],
             'brackets': len(result['opps']), 'floor': result['floor'][0],
             'near_misses': len(result['near_misses'])}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(hist_line) + '\n')
print(f"PERSISTED runs/cron_scan_{ts}.json")
