import asyncio, logging, time, json, os
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
                # CLOB asks are DESC-sorted; best ask = min price (same as detector)
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

# Persist run (git-persisted runs convention)
ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
out = {
    'run_ts_utc': ts,
    'markets': result['markets'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'near_miss_count': len(result['near_misses']),
    'near_misses_top': [{'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l}
                        for t, q, y, n, l in result['near_misses'][:10]],
    'floor': result['near_misses'][0][0] if result['near_misses'] else None,
}
os.makedirs('runs', exist_ok=True)
with open(f'runs/scan_{ts}.json', 'w') as f:
    json.dump(out, f, indent=2)
with open('runs/scan_latest.out', 'w') as f:
    f.write(json.dumps(out, indent=2))
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(out) + '\n')
print(f"\n[saved runs/scan_{ts}.json]")
