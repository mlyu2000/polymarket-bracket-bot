# Supplementary: near-misses computed with BEST (min) ask, since CLOB /book
# returns asks in DESC order — asks[0] is the worst ask (known cron-script bug).
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
    near_misses = []
    priced = 0
    best_overall = None  # (total, question, yes, no, liq)
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if best_overall is None or total < best_overall[0]:
                best_overall = (total, m.question[:60], yes_price, no_price, m.liquidity)
            if opp is None and total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'best_overall': best_overall,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"SUPP scan (min-ask): {result['markets']} markets, {result['priced']} priced, in {result['scan_time']:.1f}s")
print(f"SUPP BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  sum={o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"SUPP near-misses (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
b = result['best_overall']
if b:
    print(f"SUPP lowest sum overall: {b[0]:.3f} | Yes@{b[2]:.3f} No@{b[3]:.3f} | liq={b[4]} | {b[1]}")
