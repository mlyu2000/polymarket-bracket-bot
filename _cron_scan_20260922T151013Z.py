import asyncio, logging, time, json
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
    near_misses = []          # provided script (asks[0]) — expected to be 0
    minask_rows = []          # corrected: min-ask floor
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
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            minask_rows.append((ya + na, m.question[:60], ya, na, m.liquidity))

    minask_rows.sort()
    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': len(minask_rows),
        'opps': opps,
        'near_misses': near_misses,
        'minask_rows': minask_rows,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
nm_minask = [r for r in result['minask_rows'] if 1.0 <= r[0] <= 1.005]
sub1 = [r for r in result['minask_rows'] if r[0] < 1.0]

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}  [provided asks[0] method]")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")

print(f"📐 MIN-ASK CORRECTED (priced={result['priced']}): floor={result['minask_rows'][0][0]:.3f} | brackets={len(sub1)} | near-misses={len(nm_minask)}")
for total, q, ya, na, liq in result['minask_rows'][:5]:
    print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq:.0f} | {q}")

ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
payload = {
    'ts': ts,
    'method': 'provided(asks[0]) + detector + minask floor',
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_seconds': round(result['scan_time'], 2),
    'best_min_sum': round(result['minask_rows'][0][0], 4),
    'brackets': result['opps'],
    'near_le_1005_provided_asks0': [
        {'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l} for t, q, y, n, l in result['near_misses'][:20]
    ],
    'near_le_1005_minask': [
        {'sum': round(t, 4), 'q': q, 'yes': y, 'no': n, 'liq': l} for t, q, y, n, l in nm_minask[:30]
    ],
}
with open(f'runs/cron_scan_{ts}.json', 'w') as f:
    json.dump(payload, f, indent=1)
print(f"PERSISTED runs/cron_scan_{ts}.json")
