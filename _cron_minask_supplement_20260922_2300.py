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
    dt = time.time() - t0

    rows = []
    priced = 0
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        priced += 1
        if tot < 1.0:
            brackets.append((tot, m.question[:60], yp, np_, m.liquidity))
        rows.append((tot, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return {'n': len(markets), 'priced': priced, 'dt': dt, 'rows': rows, 'brackets': brackets}

r = asyncio.run(scan())
print(f"markets={r['n']} priced={r['priced']} time={r['dt']:.1f}s")
print(f"true brackets (min-ask sum<1.00): {len(r['brackets'])}")
for t, q, yp, np_, liq in sorted(r['brackets']):
    print(f"  BRACKET {t:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
print("floor top 10 (min-ask):")
for t, q, yp, np_, liq in r['rows'][:10]:
    print(f"  {t:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
n_le_1005 = sum(1 for row in r['rows'] if row[0] <= 1.005)
print(f"near-misses <=1.005 (min-ask): {n_le_1005}")
