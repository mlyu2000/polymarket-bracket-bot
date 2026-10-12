import asyncio, logging, json
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
    for m, (y, n) in zip(markets, all_books):
        if y and n and y.asks and n.asks:
            yp = min(float(a['price']) for a in y.asks)
            np_ = min(float(a['price']) for a in n.asks)
            rows.append((round(yp + np_, 6), m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    floor = rows[0][0] if rows else None
    band = [r for r in rows if r[0] <= 1.005]
    top20 = rows[:20]
    return {'priced': len(rows), 'floor': floor, 'band': band, 'top20': top20}

r = asyncio.run(scan())
print(json.dumps(r, default=str))
