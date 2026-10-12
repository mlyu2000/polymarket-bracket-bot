import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            priced.append((yp + np, m.question[:60], yp, np, m.liquidity))
    priced.sort()
    print(f"priced markets: {len(priced)}")
    print("best-ask floor (top 10):")
    for total, q, yp, np, liq in priced[:10]:
        flag = "BRACKET" if total < 1.0 else ("AT-1.0" if total <= 1.0001 else "")
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q} {flag}")
    under = [p for p in priced if p[0] < 1.0]
    print(f"count sum<1.00: {len(under)}")
    at1 = [p for p in priced if p[0] >= 1.0001 and p[0] <= 1.0011]
    print(f"count sum in [1.0001,1.0011] (=1.001 floor band): {len(at1)}")

asyncio.run(scan())
