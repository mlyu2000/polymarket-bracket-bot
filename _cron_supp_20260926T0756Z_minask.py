import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    near = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            priced += 1
            if tot <= 1.005:
                near.append((tot, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    return len(markets), priced, near, dt

markets_n, priced_n, near, dt = asyncio.run(scan())
print(f"[supplement] {markets_n} markets, {priced_n} priced with liq>0, best-ask (min) method, {dt:.1f}s")
print(f"[supplement] true near-misses (min-ask sum <= 1.005): {len(near)}")
for tot, q, yp, np_, liq in near[:10]:
    print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
if near:
    print(f"[supplement] floor observed: {near[0][0]:.3f}")
