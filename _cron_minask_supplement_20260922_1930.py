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
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    print(f"[min-ask floor scan] {len(markets)} markets in {time.time()-t0:.1f}s")
    print("Top 8 lowest Yes+No best-ask sums:")
    for total, q, yp, np_, liq in rows[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"True brackets (<1.000) on best asks: {len(brackets)}")
    for total, q, yp, np_, liq in brackets:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
