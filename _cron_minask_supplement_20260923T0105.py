"""Same scan, but near-miss block uses best (min) asks like the detector, so
near-miss totals reflect real ask levels instead of the DESC-sorted asks[0]."""
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

    opps = []
    near_misses_min = []
    priced = 0
    floors = []
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
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yp = min(float(a['price']) for a in yes_book.asks)
                npr = min(float(a['price']) for a in no_book.asks)
                total = yp + npr
                priced += 1
                floors.append((total, m.question[:50], yp, npr, m.liquidity))
                if total <= 1.005:
                    near_misses_min.append((total, m.question[:50], yp, npr, m.liquidity))

    near_misses_min.sort()
    floors.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses_min': near_misses_min,
        'best_floors': floors[:5],
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses ≤1.005 (min-ask): {len(result['near_misses_min'])}")
for total, q, yp, npr, liq in result['near_misses_min'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
print("📉 Tightest 5 floors (min-ask sum):")
for total, q, yp, npr, liq in result['best_floors']:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
