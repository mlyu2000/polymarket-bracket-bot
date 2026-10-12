import asyncio, json, logging, time, os
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity,
            })
            paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append({'sum': round(total, 4), 'q': m.question[:60],
                                        'yes': yes_price, 'no': no_price, 'liq': m.liquidity})

    near_misses.sort(key=lambda r: r['sum'])
    out = {
        'ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'markets': len(markets),
        'scan_time_s': round(scan_time, 1),
        'brackets': opps,
        'near_misses': near_misses,
    }
    os.makedirs('runs', exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + 'Z'
    path = 'runs/cron_scan_' + stamp + '.json'
    with open(path, 'w') as f:
        json.dump(out, f, indent=2)
    print('saved', path)
    print('brackets:', len(opps), 'near_misses:', len(near_misses),
          'floor:', near_misses[0]['sum'] if near_misses else None)

asyncio.run(scan())
