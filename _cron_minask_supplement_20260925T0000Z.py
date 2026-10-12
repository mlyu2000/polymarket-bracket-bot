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

    brackets = []
    near = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            # asks are DESC-sorted -> best ask = min
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            s = yp + np_
            rec = (s, m.question[:60], yp, np_, m.liquidity)
            if s < 1.0:
                brackets.append(rec)
            elif s <= 1.005:
                near.append(rec)
    brackets.sort()
    near.sort()
    print(f"min-ask scan: {len(markets)} markets in {dt:.1f}s")
    print(f"BRACKETS (sum<1.000): {len(brackets)}")
    for s,q,yp,np_,liq in brackets[:10]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"NEAR (<=1.005): {len(near)}")
    for s,q,yp,np_,liq in near[:10]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
