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

    # --- Supplement: near-misses/floor recomputed with BEST asks (min).
    # CLOB /book returns asks DESC-sorted, so asks[0] is the WORST ask (~0.999)
    # and the prompt near-miss block systematically overstates totals.
    # detector.py itself uses min() correctly.
    near2 = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if total <= 1.005:
                near2.append((round(total, 4), m.question[:50], yp, np_, m.liquidity))
    near2.sort()
    true_floor = near2[0][0] if near2 else None

    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'near_minask': near2,
        'priced': priced,
        'true_floor': true_floor,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

import json
json.dump({'near': result['near_minask'], 'opps': result['opps'], 'priced': result['priced'],
           'true_floor': result['true_floor'], 'scan_time': result['scan_time'],
           'markets': result['markets']},
          open('_tmp_cron_20261008T1728Z_supp_data.json', 'w'), ensure_ascii=False)
print()
print(f"=== SUPPLEMENT: best-ask (min) floor: {result['true_floor']} | priced {result['priced']}/{result['markets']} | band<=1.005: {len(result['near_minask'])} ===")
for total, q, yp, np_, liq in result['near_minask'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq {liq:.0f} | {q}")
