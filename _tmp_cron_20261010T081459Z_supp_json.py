import asyncio, json, logging
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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        rows.append((round(yp + np_, 4), m.question[:60], yp, np_, round(m.liquidity, 2)))

    rows.sort()
    priced = len(rows)
    floor = rows[0][0] if rows else None
    brackets = [r for r in rows if r[0] < 1.0]
    band = [r for r in rows if 1.0 <= r[0] <= 1.005]
    next_tier = [r for r in rows if 1.005 < r[0] <= 1.01]
    return {
        'markets': len(markets),
        'priced': priced,
        'floor': floor,
        'brackets': [list(r) for r in brackets],
        'band': [list(r) for r in band],
        'next_tier': [list(r) for r in next_tier],
    }

data = asyncio.run(scan())
with open('_tmp_cron_20261010T081459Z_supp_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(json.dumps(data, ensure_ascii=False, indent=1))
