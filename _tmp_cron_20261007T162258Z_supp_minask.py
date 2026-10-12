import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI
logging.basicConfig(level=logging.ERROR)
async def go():
    Config.validate(); api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    for m,(yb,nb) in zip(markets,books):
        if yb and nb and yb.asks and nb.asks:
            yp=min(float(a['price']) for a in yb.asks); np_=min(float(a['price']) for a in nb.asks)
            rows.append({'sum':round(yp+np_,4),'q':m.question[:60],'yes':yp,'no':np_,'liq':m.liquidity})
    rows.sort(key=lambda r:r['sum'])
    return rows
rows = asyncio.run(go())
band=[r for r in rows if r['sum']<=1.005]
print(json.dumps({'priced':len(rows),'floor':rows[0]['sum'] if rows else None,'band':len(band),
 'band_rows':band,'next_out':rows[len(band):len(band)+4],'top_liq':max((r['liq'] for r in rows),default=None)}, indent=1))
