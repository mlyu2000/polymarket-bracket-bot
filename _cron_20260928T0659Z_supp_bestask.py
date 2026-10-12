# Supplementary: true best-ask (min) near-miss picture.
# CLOB /book asks are DESC-sorted, so asks[0] overstates the best ask;
# detector.py correctly uses min(). This reports near-misses on best-ask basis.
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
    priced = 0
    floor = None
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
                'liq': m.liquidity,
            })
            paper_result = paper.execute(opp)
        elif yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if floor is None or total < floor[0]:
                floor = (total, m.question[:50], yp, np_, m.liquidity)
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps,
            'near_misses': near_misses, 'floor': floor, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"Scan (best-ask basis): {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"BRACKETS via detector (sum<1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  sum={o['sum']:.3f} edge={o['edge']:.4f} | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} sh | liq={o['liq']} | {o['q']}")
print(f"Near-misses <=1.005 (best ask): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if result['floor']:
    t, q, yp, np_, liq = result['floor']
    print(f"True floor: {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
