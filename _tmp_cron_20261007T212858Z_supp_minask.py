import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    # CLOB /book asks are DESC-sorted; the true floor is min(price)
    if not book or not getattr(book, 'asks', None):
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
    true_brackets = []   # min-ask sum < 1.00 (detector may filter by guards)
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya, na = best_ask(yes_book), best_ask(no_book)
        if ya is not None and na is not None:
            priced += 1
            total = ya + na
            if total < 1.0:
                true_brackets.append((total, m.question[:60], ya, na, m.liquidity))
            if total <= 1.005:
                near_misses.append((total, m.question[:50], ya, na, m.liquidity))
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

    near_misses.sort()
    true_brackets.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'true_brackets': true_brackets,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 MIN-ASK Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"✅ Detector BRACKETS: {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"🔧 Raw min-ask brackets (sum<1.00, any guard): {len(result['true_brackets'])}")
for total, q, ya, na, liq in result['true_brackets'][:10]:
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print(f"📊 Best min-ask totals (top 8):")
for total, q, ya, na, liq in result['near_misses'][:8]:
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
