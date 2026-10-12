import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    brackets_min = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            rows.append((tot, m.question[:50], yp, np_, m.liquidity))
            if tot < 1.0:
                brackets_min.append((tot, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    print(f"minask scan: {len(markets)} markets in {dt:.1f}s; priced={len(rows)}")
    print(f"BRACKETS via min-ask (sum<1.00): {len(brackets_min)}")
    for t,q,yp,np_,liq in sorted(brackets_min):
        print(f"  <1.00 {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("FLOOR top 10 (min-ask best):")
    for t,q,yp,np_,liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"NEAR-MISS 1.000-1.005 (min-ask): {len(nm)}")
    for t,q,yp,np_,liq in nm[:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
