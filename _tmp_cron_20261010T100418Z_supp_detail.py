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
    out = {
        'markets': len(markets),
        'priced': len(rows),
        'floor': rows[0][0] if rows else None,
        'band_le_1005': [r for r in rows if r[0] <= 1.005],
        'top20': rows[:20],
    }
    print(json.dumps(out, default=str))

asyncio.run(scan())
