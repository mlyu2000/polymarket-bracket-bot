# Cron run 2026-09-28: user-provided script verbatim (asks[0] near-miss block) + min-ask supplement.
# detector.py correctly uses min() — CLOB asks are DESC-sorted, so asks[0] = worst ask (~0.999).
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
    near_misses = []
    min_near = []
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
                # provided-script path (asks[0] = worst ask, DESC-sorted)
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                # supplement: best-ask (min) sums
                yp = min(float(a['price']) for a in yes_book.asks)
                np_ = min(float(a['price']) for a in no_book.asks)
                mt = yp + np_
                min_near.append((mt, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    min_near.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'min_near': min_near,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (asks[0], provided script, ≤1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
priced = len(result['min_near'])
print(f"📈 SUPPLEMENT best-ask (min) sums — {priced} priced markets:")
if result['min_near']:
    print(f"  FLOOR (min sum): {result['min_near'][0][0]:.4f}")
nm5 = [x for x in result['min_near'] if x[0] <= 1.005]
print(f"  Near-misses ≤1.005 (min): {len(nm5)}")
for total, q, yp, np_, liq in nm5[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
