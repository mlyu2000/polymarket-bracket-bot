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

    detected = []
    best_ask_rows = []
    priced = 0
    floor = 10.0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detected.append({'sum': opp.total_cost, 'q': m.question[:60]})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            if total < floor:
                floor = total
            if total <= 1.005:
                best_ask_rows.append((total, m.question[:50], ya, na, m.liquidity))

    best_ask_rows.sort()
    return {'markets': len(markets), 'priced': priced, 'scan_time': scan_time,
            'detected': detected, 'floor': floor, 'near': best_ask_rows}

r = asyncio.run(scan())
print(f"Markets: {r['markets']} priced: {r['priced']} in {r['scan_time']:.1f}s")
print(f"Detector BRACKETS: {len(r['detected'])}")
for d in r['detected']:
    print(f"  {d['sum']:.4f} | {d['q']}")
print(f"True floor (min-ask sum): {r['floor']:.4f}")
print(f"Best-ask near-misses (min-ask sum <=1.005): {len(r['near'])}")
for total, q, yp, np, liq in r['near'][:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
