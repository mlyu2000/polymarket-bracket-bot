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
    near_misses = []  # min-ask based (corrected)
    two_sided = 0
    yes_only = 0
    no_only = 0
    empty = 0
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
        # corrected near-miss: min(all asks) both sides
        if yes_book and no_book and yes_book.asks and no_book.asks:
            two_sided += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if total <= 1.005:
                near_misses.append((round(total,4), m.question[:60], round(yp,4), round(np_,4), m.liquidity))
        elif yes_book and yes_book.asks:
            yes_only += 1
        elif no_book and no_book.asks:
            no_only += 1
        else:
            empty += 1

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'two_sided': two_sided,
        'yes_only': yes_only,
        'no_only': no_only,
        'empty': empty,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
out = {
    'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'markets': result['markets'],
    'brackets': len(result['opps']),
    'opps': result['opps'],
    'near_misses_top': result['near_misses'][:15],
    'near_miss_count_1p005': len(result['near_misses']),
    'two_sided': result['two_sided'],
    'yes_only': result['yes_only'],
    'no_only': result['no_only'],
    'empty': result['empty'],
    'scan_time': result['scan_time'],
}
import os
os.makedirs('runs', exist_ok=True)
fn = 'runs/_tmp_cron_' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '_supp_data.json'
with open(fn, 'w') as f:
    json.dump(out, f, indent=2, default=str)
print('SAVED:', fn)

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (min-ask sum ≤1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:15]:
    print(f"  {total:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq {liq:,.0f} | {q}")
print(f"Book structure: {result['two_sided']} two-sided / {result['yes_only']} yes-only / {result['no_only']} no-only / {result['empty']} empty")
