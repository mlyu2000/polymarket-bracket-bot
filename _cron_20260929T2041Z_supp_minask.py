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
    near = []
    priced = 0
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            # BEST asks: CLOB returns asks DESC-sorted, so min() is the true best ask
            yes_p = min(float(a['price']) for a in yes_book.asks)
            no_p = min(float(a['price']) for a in no_book.asks)
            total = yes_p + no_p
            if floor is None or total < floor:
                floor = total
            if total <= 1.005:
                near.append((total, m.question[:60], yes_p, no_p, m.liquidity))

    near.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps, 'near': near,
            'floor': floor, 'scan_time': scan_time}

r = asyncio.run(scan())
print(f"[min-ask supplemental] {r['markets']} markets ({r['priced']} priced) in {r['scan_time']:.1f}s")
print(f"BRACKETS (best-ask sum < 1.00): {len(r['opps'])}")
for s, e, sh, q, liq in sorted(r['opps']):
    print(f"  sum={s:.4f} edge={e:.4f} shares={sh} liq={liq} | {q}")
print(f"True floor (best-ask sum): {r['floor']:.4f}" if r['floor'] else "no priced markets")
print(f"Near-misses (best-ask sum <= 1.005): {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:10]:
    print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
