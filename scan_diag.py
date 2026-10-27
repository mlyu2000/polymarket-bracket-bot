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
    near_misses_asks0 = []     # artifact: asks[0] = worst/highest ask
    near_misses_minask = []   # correct: best (min) ask
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
                # correct min-ask diagnostic
                y_best = min(yes_book.asks, key=lambda a: float(a["price"]))
                n_best = min(no_book.asks, key=lambda a: float(a["price"]))
                y_min = float(y_best["price"])
                n_min = float(n_best["price"])
                total_min = y_min + n_min
                if total_min <= 1.005:
                    near_misses_minask.append((total_min, m.question[:60], "min", y_min, n_min, m.liquidity))
                # artifact check: asks[0]
                y0 = float(yes_book.asks[0]["price"])
                n0 = float(no_book.asks[0]["price"])
                total0 = y0 + n0
                if total0 <= 1.005:
                    near_misses_asks0.append((total0, m.question[:60], "asks0", y0, n0, m.liquidity))

    near_misses_minask.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'minask_near_misses': near_misses_minask,
        'asks0_near_misses': near_misses_asks0,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00, min-ask): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq {o['liq']:.0f} | {o['q']}")
print(f"📊 MIN-ASK near-misses (≤1.005): {len(result['minask_near_misses'])}")
for total, q, _, yp, np, liq in result['minask_near_misses']:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq {liq:.0f} | {q}")
print(f"📉 ASKS0 (artifact) near-misses (≤1.005): {len(result['asks0_near_misses'])}")
for total, q, _, yp, np, liq in result['asks0_near_misses']:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq {liq:.0f} | {q}")
