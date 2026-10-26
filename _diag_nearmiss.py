import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses_minask = []
    near_misses_asks0 = []
    two_sided_count = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            two_sided_count += 1
            # Correct: min of all asks
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            total_min = yes_min + no_min
            if total_min <= 1.005:
                near_misses_minask.append((total_min, m.question[:50], yes_min, no_min, m.liquidity))
            # Script's approach: asks[0]
            yes0 = float(yes_book.asks[0]['price'])
            no0 = float(no_book.asks[0]['price'])
            total0 = yes0 + no0
            if total0 <= 1.005:
                near_misses_asks0.append((total0, m.question[:50], yes0, no0, m.liquidity))

    near_misses_minask.sort()
    near_misses_asks0.sort()
    return {
        'markets': len(markets),
        'scan_time': scan_time,
        'opps': len(opps),
        'two_sided': two_sided_count,
        'near_misses_minask': near_misses_minask,
        'near_misses_asks0': near_misses_asks0,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {result['opps']}")
print(f"📊 Two-sided books: {result['two_sided']}")
print(f"📊 Near-misses (min-ask, ≤1.005): {len(result['near_misses_minask'])}")
for total, q, yp, np, liq in result['near_misses_minask'][:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📊 Near-misses (asks[0], ≤1.005): {len(result['near_misses_asks0'])}")
for total, q, yp, np, liq in result['near_misses_asks0'][:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
