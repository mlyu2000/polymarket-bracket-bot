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

    priced = 0
    brackets = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # TRUE best ask: CLOB asks are DESC-sorted, so min() = best ask
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total < 1.0:
            brackets.append((total, m.question[:70], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:70], yp, np_, m.liquidity))

    brackets.sort()
    near.sort()
    return {'markets': len(markets), 'priced': priced, 'brackets': brackets,
            'near': near, 'scan_time': scan_time}

r = asyncio.run(scan())
print(f"markets={r['markets']} priced={r['priced']} scan={r['scan_time']:.1f}s")
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(r['brackets'])}")
for t, q, yp, np_, liq in r['brackets'][:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"NEAR-MISS (<=1.005): {len(r['near'])}")
for t, q, yp, np_, liq in r['near'][:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
