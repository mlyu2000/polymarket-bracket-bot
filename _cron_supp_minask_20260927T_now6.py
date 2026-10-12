import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
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
    min_total = None
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
            paper.execute(opp)
        ya = best_ask(yes_book)
        na = best_ask(no_book)
        if ya is not None and na is not None:
            total = ya + na
            if min_total is None or total < min_total[0]:
                min_total = (total, m.question[:60], ya, na, m.liquidity)
            if total <= 1.005:
                near_misses.append((total, m.question[:50], ya, na, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'min_total': min_total,
    }

result = asyncio.run(scan())
print(f"🔍 MIN-ASK Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (min-ask sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (min-ask ≤1.005): {len(result['near_misses'])}")
for total, q, yp, npr, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npr:.3f} | {q}")
if result['min_total']:
    t, q, yp, npr, liq = result['min_total']
    print(f"📉 Global min-ask floor: {t:.3f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
