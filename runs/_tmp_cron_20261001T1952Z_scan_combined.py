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
    best_sums = []
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # verbatim asks[0] (worst ask; CLOB lists asks DESC)
            yp0 = float(yes_book.asks[0]['price']); np0 = float(no_book.asks[0]['price'])
            t0sum = yp0 + np0
            if t0sum <= 1.005:
                near_misses.append((t0sum, m.question[:50], yp0, np0, m.liquidity))
            # correct: best ask = min price
            yb = min(yes_book.asks, key=lambda a: float(a['price']))
            nb = min(no_book.asks, key=lambda a: float(a['price']))
            yp = float(yb['price']); np = float(nb['price'])
            if 0 < yp < 1 and 0 < np < 1:
                best_sums.append((round(yp+np,4), m.question[:55], yp, np, m.liquidity,
                                  int(float(yb['size'])), int(float(nb['size']))))
    near_misses.sort()
    best_sums.sort()
    return {'markets': len(markets), 'opps': opps, 'near_misses': near_misses,
            'best_sums': best_sums, 'scan_time': scan_time}

r = asyncio.run(scan())
print(f"Scan: {r['markets']} markets in {r['scan_time']:.1f}s")
print(f"BRACKETS (detector, net_edge>=margin): {len(r['opps'])}")
for o in r['opps']:
    print(f"  BRACKET sum={o['sum']:.3f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']:.0f} | {o['q']}")
print(f"Near-misses verbatim asks[0] (<=1.005): {len(r['near_misses'])}")
for total, q, yp, np, liq in r['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"\n--- best-ask (min) floor: valid pairs={len(r['best_sums'])} ---")
for s, q, yp, np, liq, ys, ns in r['best_sums'][:8]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} sz={min(ys,ns)} | {q}")
lt1 = [x for x in r['best_sums'] if x[0] < 1.0]
rng = [x for x in r['best_sums'] if 1.0 <= x[0] <= 1.005]
print(f"best-ask sums < 1.00: {len(lt1)} | in [1.000,1.005]: {len(rng)}")
for s, q, yp, np, liq, ys, ns in lt1:
    print(f"  SUB-1.00: {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} sz={min(ys,ns)} | {q}")
