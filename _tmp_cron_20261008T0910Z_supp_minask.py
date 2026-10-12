import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    floors = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            s = yp + np_
            priced += 1
            floors.append((s, m.question[:55], yp, np_, m.liquidity))
    floors.sort()
    return len(markets), priced, floors

markets_n, priced_n, floors = asyncio.run(scan())
print(f"Best-ask (min) floor scan over {priced_n}/{markets_n} priced markets")
brackets = [f for f in floors if f[0] < 1.0]
near = [f for f in floors if 1.0 <= f[0] <= 1.005]
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(brackets)}")
for s, q, yp, np_, liq in brackets[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"TRUE NEAR-MISSES (1.00 <= sum <= 1.005): {len(near)}")
for s, q, yp, np_, liq in near[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"GLOBAL MIN: {floors[0][0]:.4f} | {floors[0][1]}")
for s, q, yp, np_, liq in floors[1:8]:
    print(f"  floor {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
