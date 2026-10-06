import asyncio, json, logging, time
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
    band = [x for x in sums if 1.0 <= x[0] <= 1.005]
    print(f"sum<1.00: {len(lt1)} | band[1.000,1.005]: {len(band)}")
    for s, q, yp, npx, ysz, nsz, liq in lt1:
        print(f"  *** sum={s:.4f} | Yes@{yp:.3f}(x{ysz}) No@{npx:.3f}(x{nsz}) | liq={liq} | {q}")
    return {
        'markets': len(markets),
        'priced': priced,
        'floor': sums[0][0] if sums else None,
        'brackets_minask': len(lt1),
        'band_minask': len(band),
        'top': [{'sum': round(s,4), 'q': q, 'yes': yp, 'no': npx, 'ysz': ysz, 'nsz': nsz, 'liq': liq} for s,q,yp,npx,ysz,nsz,liq in sums[:10]],
    }

data = asyncio.run(supp())
with open('runs/_tmp_cron_20261006T0713Z_supp_data.json','w') as f:
    json.dump(data, f, indent=1)
