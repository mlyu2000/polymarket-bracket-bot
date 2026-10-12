import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI(); detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    sums = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            npr = min(float(a['price']) for a in nb.asks)
            priced += 1
            sums.append((yp+npr, m.question[:50], yp, npr, m.liquidity))
    sums.sort()
    print(f"supp scan {time.time()-t0:.1f}s | priced={priced}/{len(markets)}")
    print("best min-ask sums:")
    for s in sums[:8]:
        print(f"  {s[0]:.4f} | Yes@{s[2]:.3f} No@{s[3]:.3f} | liq={s[4]} | {s[1]}")
    under1 = [s for s in sums if s[0] < 1.0]
    print(f"min-ask sums < 1.00: {len(under1)}")
    for s in under1[:10]:
        print(f"  ⚠️ {s[0]:.4f} | Yes@{s[2]:.3f} No@{s[3]:.3f} | liq={s[4]} | {s[1]}")

asyncio.run(supp())
