import asyncio, logging, time, json
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
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({'q': m.question[:60], 'sum': opp.total_cost, 'edge': opp.net_edge,
                         'yes': opp.yes_price, 'no': opp.no_price, 'shares': opp.max_shares})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            rows.append((total, m.question[:50], yp, np_, m.liquidity))
            if total <= 1.005 and opp is None:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    near.sort()
    return markets, opps, near, rows, scan_time

markets, opps, near, rows, scan_time = asyncio.run(scan())
print(f"MIN-ASK SCAN: {len(markets)} markets priced, {len(rows)} with both-side asks, {scan_time:.1f}s")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(opps)}")
for o in opps:
    print(f"  {o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh | {o['q']}")
print(f"TRUE NEAR-MISSes (min-ask sum <= 1.005): {len(near)}")
for t, q, yp, np_, liq in near[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("BOTTOM 10 FLOORS:")
for t, q, yp, np_, liq in rows[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
