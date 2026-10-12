import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    nms = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            npr = min(float(a['price']) for a in nb.asks)
            t = yp + npr
            if t <= 1.005:
                nms.append((t, m.question[:50], yp, npr, m.liquidity))
    nms.sort()
    return priced, nms

priced, nms = asyncio.run(scan())
print(f"Markets with both books priced (min-ask): {priced}")
print(f"Near-misses (min-ask sum <= 1.005): {len(nms)}")
for t, q, yp, np, liq in nms[:10]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
