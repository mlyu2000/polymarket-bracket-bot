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
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.liquidity, m.question[:60]))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # FIXED near-miss: asks are DESC-sorted; use min() like detector does
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    opps.sort()
    near_misses.sort()
    return {'markets': len(markets), 'opps': opps, 'near_misses': near_misses, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"[min-ask supplement] Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (detector, sum<1.00): {len(result['opps'])}")
for s, e, yp, np, sh, liq, q in result['opps'][:10]:
    print(f"  sum={s:.4f} edge={e:.4f} Yes@{yp:.3f} No@{np:.3f} shares={sh} liq={liq} | {q}")
print(f"Near-misses (<=1.005, min-ask): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if result['near_misses']:
    print(f"FLOOR (lowest min-ask sum): {result['near_misses'][0][0]:.4f}")
