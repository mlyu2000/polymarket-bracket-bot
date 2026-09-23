import asyncio, logging, time, json, os
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    # CLOB asks are DESC-sorted; asks[0] is the WORST ask. Use min().
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)

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
        else:
            yp = best_ask(yes_book)
            np_ = best_ask(no_book)
            if yp is not None and np_ is not None:
                priced += 1
                total = yp + np_
                if floor is None or total < floor:
                    floor = total
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'floor': floor,
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s ({result['priced']} with two-sided asks, true floor sum={result['floor']:.3f})")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

os.makedirs('runs', exist_ok=True)
stamp = time.strftime('%Y%m%dT%H%MZ', time.gmtime())
with open(f'runs/cron_{stamp}.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"[persisted runs/cron_{stamp}.json]")
