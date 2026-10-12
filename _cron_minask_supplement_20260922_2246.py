# Known cron-script bug (see memory): near-miss block uses asks[0] which is the
# WORST ask (asks are DESC-sorted on CLOB /book). Supplement with true best asks.
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
    sums = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            sums.append((yp+np_, m.question[:55], yp, np_, m.liquidity))
    sums.sort()
    print(f"markets with best-ask sums: {len(sums)} in {time.time()-t0:.1f}s")
    print(f"BRACKETS (best-ask sum < 1.00): {sum(1 for s in sums if s[0] < 1.0)}")
    print("Top 8 lowest best-ask sums:")
    for total, q, yp, np_, liq in sums[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
