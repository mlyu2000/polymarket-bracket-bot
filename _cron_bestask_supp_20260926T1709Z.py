import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets = []
    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append({
                'total': opp.total_cost, 'q': m.question[:50],
                'yes': opp.yes_price, 'no': opp.no_price,
                'edge': opp.net_edge, 'shares': opp.max_shares, 'liq': m.liquidity
            })
        elif yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            tot = round(yp + np_, 4)
            priced += 1
            if tot <= 1.005:
                near_misses.append({'total': tot, 'q': m.question[:50], 'yes': yp, 'no': np_, 'liq': m.liquidity})

    near_misses.sort(key=lambda d: d['total'])
    return {'run_utc': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()),
            'markets': len(markets), 'priced': priced,
            'brackets_lt_1': brackets, 'near_misses_le_1005': near_misses}

out = asyncio.run(scan())
fn = 'runs/cron_scan_' + time.strftime('%Y%m%dT%H%MZ', time.gmtime()) + '.json'
with open(fn, 'w') as f:
    json.dump(out, f, indent=2)
print(fn)
print(json.dumps({'markets': out['markets'], 'priced': out['priced'],
                  'brackets': len(out['brackets_lt_1']),
                  'near_misses': len(out['near_misses_le_1005']),
                  'floor': out['near_misses_le_1005'][0]['total'] if out['near_misses_le_1005'] else None}))
