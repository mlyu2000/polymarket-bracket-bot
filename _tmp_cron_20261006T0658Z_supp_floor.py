import asyncio, logging
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    sums = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        ya = min(yb.asks, key=lambda a: float(a['price']))
        na = min(nb.asks, key=lambda a: float(a['price']))
        yp, npx = float(ya['price']), float(na['price'])
        sums.append((yp + npx, m.question[:60], yp, npx, int(float(ya['size'])), int(float(na['size'])), m.liquidity))
    sums.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print("TRUE best-ask floors (sum=Yes+No), 8 lowest:")
    for s, q, yp, npx, ysz, nsz, liq in sums[:8]:
        print(f"  sum={s:.4f} | Yes@{yp:.3f}(x{ysz}) No@{npx:.3f}(x{nsz}) | liq={liq} | {q}")
    lt1 = [x for x in sums if x[0] < 1.0]
    le1001 = [x for x in sums if x[0] <= 1.001]
    print(f"sum<1.00: {len(lt1)} | sum<=1.001: {len(le1001)}")
    for s, q, yp, npx, ysz, nsz, liq in lt1:
        print(f"  *** sum={s:.4f} | Yes@{yp:.3f}(x{ysz}) No@{npx:.3f}(x{nsz}) | liq={liq} | {q}")

asyncio.run(supp())
