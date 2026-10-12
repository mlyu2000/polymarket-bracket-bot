import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    totals = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            totals.append((y + n, y, n, m.question[:70], m.liquidity))
    totals.sort()
    print(f"priced markets: {len(totals)}")
    brackets = [t for t in totals if t[0] < 1.0]
    print(f"true brackets (min-ask sum < 1.0): {len(brackets)}")
    print("floor (best min-ask sums):")
    for s, y, n, q, liq in totals[:10]:
        print(f"  sum={s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    under1005 = [t for t in totals if t[0] <= 1.005]
    print(f"near-misses (sum <= 1.005): {len(under1005)}")
    for s, y, n, q, liq in under1005[:10]:
        print(f"  sum={s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(scan())
