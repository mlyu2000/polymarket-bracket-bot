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

    all_rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        row = (tot, m.question[:60], yp, np_, m.liquidity)
        all_rows.append(row)
        if tot < 1.0:
            ys = max(float(a['size']) for a in yb.asks if float(a['price']) == yp)
            ns = max(float(a['size']) for a in nb.asks if float(a['price']) == np_)
            brackets.append((tot, m.question[:60], yp, np_, min(int(ys), int(ns)), m.liquidity))

    all_rows.sort()
    brackets.sort()
    return markets, all_rows, brackets, scan_time

markets, all_rows, brackets, scan_time = asyncio.run(scan())
priced = len(all_rows)
near = [r for r in all_rows if r[0] <= 1.005]
print(f"Best-ask supplement: {priced}/{len(markets)} markets priced in {scan_time:.1f}s")
print(f"TRUE BRACKETS (best-ask sum<1.00): {len(brackets)}")
for tot, q, yp, np_, sh, liq in brackets[:10]:
    print(f"  RED sum={tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | {sh} sh | liq={liq} | {q}")
print(f"Near-misses (best-ask sum<=1.005): {len(near)}")
for tot, q, yp, np_, liq in near[:10]:
    print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if all_rows:
    tot, q, yp, np_, liq = all_rows[0]
    print(f"Floor: lowest total across all priced markets = {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
