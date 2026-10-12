import asyncio, logging, time
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

    # Corrected near-miss/floor check: CLOB asks are DESC-sorted, so use min()
    # over each side's asks (asks[0] is the WORST ask ~0.999).
    strict = []      # true brackets: min sum < 1.00
    near = []        # 1.00 < min sum <= 1.005
    priced = 0
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        priced += 1
        sums.append(total)
        row = (total, m.question[:50], yes_min, no_min, m.liquidity)
        if total < 1.0:
            strict.append(row)
        elif total <= 1.005:
            near.append(row)

    strict.sort(); near.sort(); sums.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'strict': strict,
        'near': near,
        'floor': sums[0] if sums else None,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Corrected scan (min-ask): {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"✅ TRUE BRACKETS (min sum < 1.00): {len(result['strict'])}")
for total, q, yp, np, liq in result['strict'][:10]:
    print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"📊 Near-misses (1.00..1.005): {len(result['near'])}")
for total, q, yp, np, liq in result['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"📉 Best floor across all priced markets: {result['floor']}")
