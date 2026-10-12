import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        yp, np = best_ask(yb), best_ask(nb)
        if yp is None or np is None:
            continue
        rows.append({'total': yp + np, 'q': m.question, 'yes': yp, 'no': np, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['total'])
    json.dump(rows, open('_tmp_cron_20261009T2305Z_supp_data.json', 'w'))
    print("supp rows:", len(rows))

asyncio.run(supp())
