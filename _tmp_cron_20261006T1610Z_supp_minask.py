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
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        ysz = next(float(a['size']) for a in yb.asks if float(a['price'])==yp)
        nsz = next(float(a['size']) for a in nb.asks if float(a['price'])==np_)
        rows.append((yp+np_, m.question[:60], yp, np_, ysz, nsz))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print("--- TRUE best-ask floors (top 10) ---")
    for t,q,yp,np_,ysz,nsz in rows[:10]:
        flag = "<<< BRACKET" if t < 1.0 else ""
        print(f"  {t:.4f} | Yes@{yp:.3f}(sz{ysz:.0f}) No@{np_:.3f}(sz{nsz:.0f}) | {q} {flag}")
    print(f"--- counts: sum<1.0: {sum(1 for r in rows if r[0]<1.0)} | <=1.005: {sum(1 for r in rows if r[0]<=1.005)} | <=1.01: {sum(1 for r in rows if r[0]<=1.01)}")

asyncio.run(scan())
