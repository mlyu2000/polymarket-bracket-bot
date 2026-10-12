import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    sums = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            npr = min(float(a['price']) for a in nb.asks)
            sums.append((yp+npr, m.question[:55], yp, npr, m.liquidity))
    sums.sort()
    print(f"priced markets: {len(sums)} / {len(markets)}")
    print("floor (min-ask best sums):")
    for s,q,yp,npr,liq in sums[:5]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
    brackets = [x for x in sums if x[0] < 1.0]
    print(f"true brackets (sum<1.00): {len(brackets)}")

asyncio.run(main())
