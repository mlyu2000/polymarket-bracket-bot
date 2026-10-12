import asyncio, json, logging, time
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
    near_misses_minask = []
    rows = []
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
                # asks[0] variant (as provided in the task script)
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                # min-ask variant (correct best ask; asks are DESC-sorted)
                yp = min(float(a['price']) for a in yes_book.asks)
                np_ = min(float(a['price']) for a in no_book.asks)
                tot = yp + np_
                rows.append({'sum': tot, 'q': m.question[:55], 'yes': yp, 'no': np_, 'liq': m.liquidity})
                if tot <= 1.005:
                    near_misses_minask.append((tot, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    near_misses_minask.sort()
    rows.sort(key=lambda r: r['sum'])
    return {
        'markets': len(markets),
        'priced': len(rows),
        'opps': opps,
        'near_misses': near_misses,
        'near_misses_minask': near_misses_minask,
        'best_min_sum': rows[0]['sum'] if rows else None,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out = {
    'ts': ts, 'method': 'detector-minask + provided(asks[0]) + minask supplement',
    'markets': result['markets'], 'priced': result['priced'],
    'scan_seconds': result['scan_time'],
    'best_min_sum': result['best_min_sum'],
    'brackets': result['opps'],
    'near_le_1005_minask': [{'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l}
                            for t, q, y, n, l in result['near_misses_minask']],
    'near_le_1005_asks0': [{'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l}
                           for t, q, y, n, l in result['near_misses']],
}
path = f'runs/cron_scan_{ts}.json'
with open(path, 'w') as f:
    json.dump(out, f, indent=1)

print(f"SAVED {path}")
print(f"🔍 Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
nm = result['near_misses_minask']
print(f"📊 Near-misses (≤1.005, min-ask): {len(nm)}")
for total, q, yp, np_, liq in nm[:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"(provided-script asks[0] near-misses: {len(result['near_misses'])})")
print(f"best_min_sum={result['best_min_sum']}")
