import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} markets")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    for idx, (m, (yes_book, no_book)) in enumerate(zip(markets, all_books)):
        if not yes_book or not no_book:
            continue
        # Use min ask logic as detector does
        if not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        if total < 1.0:
            opps.append((total, m.question[:80], yes_price, no_price, m.liquidity))
        elif total <= 1.005:
            near_misses.append((total, m.question[:80], yes_price, no_price, m.liquidity))

    near_misses.sort(key=lambda x: x[0])
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for total, q, yp, np, liq in result['opps']:
    print(f"  🔴 {total:.4f} | Yes@{yp:.4f} No@{np:.4f} | liq {liq} | {q}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.4f} No@{np:.4f} | liq {liq} | {q}")
