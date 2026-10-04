"""Cron run 2026-10-04T1609Z.

Part A: user-provided scan script verbatim (asks[0] near-misses + paper exec).
Part B: mechanism-agnostic min-ask floor supplement over the SAME books
        (asks[0] on the CLOB is the WORST ask -- descending sort -- so the
        provided near-miss block under-reports; detector.py uses min() and
        is correct).
"""
import asyncio, logging, time, json
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
    minask_near = []
    priced = 0
    rows = []
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

                # supplement: best (min) ask on each side
                ya = min(float(a['price']) for a in yes_book.asks)
                na = min(float(a['price']) for a in no_book.asks)
                priced += 1
                t2 = ya + na
                rows.append((t2, m.question[:55], ya, na, m.liquidity))
                if t2 <= 1.005:
                    minask_near.append((t2, m.question[:50], ya, na, m.liquidity))

    near_misses.sort()
    rows.sort()
    minask_near.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'minask_near': minask_near,
        'priced': priced,
        'rows10': rows[:10],
        'count_le_1010': sum(1 for r in rows if r[0] <= 1.010),
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  ** {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"Near-misses (<=1.005, provided asks[0] method): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print("--- Supplement: min-ask method ---")
print(f"Both-sides-priced: {result['priced']}")
print(f"Min-ask near-misses (<=1.005): {len(result['minask_near'])}")
for total, q, ya, na, liq in result['minask_near'][:10]:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
print(f"count sum<=1.010: {result['count_le_1010']}")
print("Lowest 10 min-ask sums (floor):")
for total, q, ya, na, liq in result['rows10']:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")

with open('_tmp_cron_20261004T1609Z_scan_data.json', 'w') as f:
    json.dump(result, f, default=str)
