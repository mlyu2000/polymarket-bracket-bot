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
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()

    # Supplemental: min-ask based near-misses (asks[0] is worst ask in CLOB payload)
    min_near = []
    best_min_sum = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yes_book.asks)
            npr = min(float(a['price']) for a in no_book.asks)
            tot = yp + npr
            if best_min_sum is None or tot < best_min_sum[0]:
                best_min_sum = (tot, m.question[:50], yp, npr, m.liquidity)
            if tot <= 1.005:
                min_near.append((tot, m.question[:50], yp, npr, m.liquidity))
    min_near.sort()

    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'min_near': min_near,
        'best_min_sum': best_min_sum,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"🧮 SUPPLEMENTAL min-ask near-misses (≤1.005): {len(result['min_near'])}")
for total, q, yp, npr, liq in result['min_near'][:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
if result['best_min_sum']:
    t, q, yp, npr, liq = result['best_min_sum']
    print(f"  best min-ask sum: {t:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
