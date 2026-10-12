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
    both = 0; yes_only = 0; no_only = 0; empty = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        y_asks = yes_book.asks if yes_book else []
        n_asks = no_book.asks if no_book else []
        if y_asks and n_asks:
            both += 1
            y_min = min(float(a['price']) for a in y_asks)
            n_min = min(float(a['price']) for a in n_asks)
            total = y_min + n_min
            rows.append((total, m.question[:60], y_min, n_min, m.liquidity, len(y_asks), len(n_asks)))
        elif y_asks:
            yes_only += 1
        elif n_asks:
            no_only += 1
        else:
            empty += 1
    rows.sort()
    top = rows[:15]
    out = {
        'structural': {'both': both, 'yes_only': yes_only, 'no_only': no_only, 'empty': empty},
        'n_le_1010': sum(1 for r in rows if r[0] <= 1.010),
        'n_le_1005': sum(1 for r in rows if r[0] <= 1.005),
        'n_lt_1': sum(1 for r in rows if r[0] < 1.0),
        'top': [
            {'total': round(r[0],4), 'q': r[1], 'yes': round(r[2],4), 'no': round(r[3],4), 'liq': r[4]}
            for r in top
        ],
    }
    print(json.dumps(out, indent=1))

asyncio.run(scan())
