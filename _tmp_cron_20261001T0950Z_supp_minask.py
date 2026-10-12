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

    brackets = []
    priced = 0
    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            totals.append((yp+np_, m.question[:55], yp, np_, m.liquidity))
    totals.sort()
    return {'markets': len(markets), 'priced': priced, 'brackets': brackets, 'totals': totals, 't': scan_time}

r = asyncio.run(scan())
print(f"Best-ask scan: {r['markets']} markets ({r['priced']} priced) in {r['t']:.1f}s")
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(r['brackets'])}")
for s,e,sh,q in r['brackets']:
    print(f"  RED sum={s:.4f} edge={e:.4f} shares={sh} | {q}")
print(f"Near-misses best-ask <=1.005: {sum(1 for t in r['totals'] if t[0] <= 1.005)}")
print("Top-10 lowest best-ask totals:")
for total, q, yp, np_, liq in r['totals'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
