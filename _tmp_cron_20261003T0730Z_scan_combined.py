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
    # supplement: true best-ask (min) totals for floor tracking
    floor_rows = []
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
                # min-ask floor row (best ask across levels)
                yb = min(yes_book.asks, key=lambda a: float(a['price']))
                nb = min(no_book.asks, key=lambda a: float(a['price']))
                ft = float(yb['price']) + float(nb['price'])
                floor_rows.append((ft, m.question[:50], float(yb['price']), float(nb['price']), m.liquidity))

    near_misses.sort()
    floor_rows.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'floor_rows': floor_rows,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (detected, sum<1 after buffers): {len(result['opps'])}")
for o in result['opps']:
    print(f"  R {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"Near-misses (asks[0], <=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"SUPP best-ask(min) floor: priced={len(result['floor_rows'])}")
if result['floor_rows']:
    print(f"  MIN SUM = {result['floor_rows'][0][0]:.4f}")
    for ft, q, yp, np, liq in result['floor_rows'][:8]:
        print(f"  {ft:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    below1 = [r for r in result['floor_rows'] if r[0] < 1.0]
    print(f"  raw min-sums below 1.000: {len(below1)}")
    for ft, q, yp, np, liq in below1[:10]:
        print(f"    {ft:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
