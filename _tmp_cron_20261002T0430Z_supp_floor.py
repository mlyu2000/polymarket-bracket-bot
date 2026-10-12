import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    # Corrected near-miss: best ask = min(asks) (CLOB lists asks DESC)
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        rows.append((total, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    return {'markets': len(markets), 'priced': priced, 'rows': rows, 't': scan_time}

r = asyncio.run(scan())
print(f"Markets: {r['markets']} | priced with both books: {r['priced']} | {r['t']:.1f}s")
print("TRUE floor (min-ask sums, best 10):")
for total, q, yp, np, liq in r['rows'][:10]:
    tag = " <1.00 BRACKET" if total < 1.0 else (" <=1.005 near" if total <= 1.005 else "")
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq}{tag} | {q}")
n5 = [x for x in r['rows'] if x[0] <= 1.005]
n0 = [x for x in r['rows'] if x[0] < 1.0]
print(f"Near-misses (<=1.005, min-ask): {len(n5)} | Brackets (<1.00): {len(n0)}")
