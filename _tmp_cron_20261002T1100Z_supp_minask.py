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
    near = []
    brackets = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        tot = yp + np
        priced += 1
        if tot < 1.0:
            brackets.append((tot, yp, np, m.liquidity, m.question[:60]))
        elif tot <= 1.005:
            near.append((tot, yp, np, m.liquidity, m.question[:50]))
    near.sort(); brackets.sort()
    return priced, brackets, near, dt

priced, brackets, near, dt = asyncio.run(scan())
print(f"min-ask supplement: {priced} priced books in {dt:.1f}s")
print(f"true brackets (sum<1.00): {len(brackets)}")
for tot, yp, np, liq, q in brackets[:10]:
    print(f"  [BRACKET] {tot:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"near-misses (<=1.005): {len(near)}")
for tot, yp, np, liq, q in near[:10]:
    print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
