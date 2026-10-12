# Supplementary: correct near-miss floor using MIN asks (asks[0] is worst due to DESC sort)
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
    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            totals.append((yp + np_, m.question[:50], yp, np_, m.liquidity))

    totals.sort()
    return {'markets': len(markets), 'opps': opps, 'totals': totals, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"[min-ask] Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"[min-ask] TRUE BRACKETS via detector (sum<1.00): {len(result['opps'])}")
for s, e, yp, np_, sh, q, liq in sorted(result['opps']):
    print(f"  sum={s:.4f} edge={e:.4f} Yes@{yp:.3f} No@{np_:.3f} shares={sh} liq={liq} | {q}")
print(f"[min-ask] TOP 8 LOWEST BEST-ASK SUMS:")
for total, q, yp, np_, liq in result['totals'][:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
nm = [t for t in result['totals'] if t[0] <= 1.005]
print(f"[min-ask] near-misses (<=1.005): {len(nm)}")
