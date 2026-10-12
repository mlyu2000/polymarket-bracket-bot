import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    def best_ask(book):
        if not book or not getattr(book, 'asks', None):
            return None
        try:
            return min(float(a['price']) for a in book.asks)
        except Exception:
            return None

    floors = []
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya, na = best_ask(yb), best_ask(nb)
        if ya is None and na is None:
            empty += 1
        elif ya is None:
            yes_only += 1
        elif na is None:
            no_only += 1
        else:
            two_sided += 1
            floors.append((ya + na, m.question[:50], ya, na, m.liquidity))
    floors.sort()
    data = {
        'markets': len(markets),
        'scan_time': round(scan_time, 1),
        'two_sided': two_sided,
        'yes_only': yes_only,
        'no_only': no_only,
        'empty': empty,
        'floor_top': [
            {'sum': round(f, 4), 'q': q, 'yes': y, 'no': n, 'liq': l}
            for f, q, y, n, l in floors[:8]
        ],
    }
    with open('_tmp_cron_20261011Tnow_supp_data.json', 'w') as fp:
        json.dump(data, fp, indent=2)
    print(json.dumps(data, indent=2))

asyncio.run(scan())
