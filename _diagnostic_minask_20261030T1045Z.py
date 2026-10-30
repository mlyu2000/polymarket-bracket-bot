"""
Diagnostic: corrected near-miss computation using min(all asks) instead of
asks[0]. Per knowledge base: 'asks[0] artifact' inflates totals, suppressing
near-misses; 'diag min-ask is source of truth'; median 2-sided min-ask ~1.03.
Also computes floor (min yes-ask + min no-ask) and two-sided bracket count.
"""
import asyncio, logging, time, statistics
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

    # Bracket opps (uses detector's correct min() logic)
    opps = []
    # Corrected near-misses with min(all asks)
    near_min = []
    # Asks[0] artifact near-misses (what the user-provided script computed)
    near_asks0 = []
    # Floor per market = min yes-ask + min no-ask
    floors = []
    two_sided = 0         # both sides have asks
    yes_only = 0
    no_only = 0
    none_both = 0

    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)

        has_yes_asks = yes_book and yes_book.asks
        has_no_asks = no_book and no_book.asks
        if has_yes_asks and has_no_asks:
            two_sided += 1
        elif has_yes_asks and not has_no_asks:
            yes_only += 1
        elif has_no_asks and not has_yes_asks:
            no_only += 1
        else:
            none_both += 1

        if has_yes_asks and has_no_asks:
            y_min = min(float(a['price']) for a in yes_book.asks)
            n_min = min(float(a['price']) for a in no_book.asks)
            floor = y_min + n_min
            floors.append(floor)
            tot_min = y_min + n_min
            tot_ask0 = float(yes_book.asks[0]['price']) + float(no_book.asks[0]['price'])
            if tot_min <= 1.005:
                near_min.append((tot_min, y_min, n_min, floor, m.question[:55], m.liquidity))
            if tot_ask0 <= 1.005:
                near_asks0.append((tot_ask0, float(yes_book.asks[0]['price']), float(no_book.asks[0]['price']), m.question[:55], m.liquidity))

    floors.sort()
    return {
        'markets': len(markets),
        'bonds': len(opps),
        'near_min': near_min,
        'near_asks0': near_asks0,
        'floors': floors,
        'scan_time': scan_time,
        'two_sided': two_sided,
        'yes_only': yes_only,
        'no_only': no_only,
        'none_both': none_both,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s  (500 max, sorted by volume)")
print(f"✅ BRACKETS (sum < 1.00, detector min-ask): {result['bonds']}")
print(f"📊 Near-misses (≤1.005, CORRECTED min(all asks)): {len(result['near_min'])}")
for total, yp, np, floor, q, liq in result['near_min'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} floor={floor:.4f} | {q}")
print(f"📊 Near-misses (≤1.005, asks[0] ARTIFACT): {len(result['near_asks0'])}")
print(f"🧮 Floor stats: n={len(result['floors'])} min={result['floors'][0]:.4f} max={result['floors'][-1]:.4f} "
      f"median={statistics.median(result['floors']):.4f} mean={statistics.mean(result['floors']):.4f}")
floors_le1005 = sum(1 for f in result['floors'] if f <= 1.005)
floors_le1010 = sum(1 for f in result['floors'] if f <= 1.010)
print(f"🧮 Floors ≤1.005: {floors_le1005}  | ≤1.010: {floors_le1010}")
print(f"🧭 Book shape: two_sided={result['two_sided']} yes_only={result['yes_only']} no_only={result['no_only']} none={result['none_both']}")
