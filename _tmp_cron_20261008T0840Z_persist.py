import asyncio, json, time, shutil, logging, os
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    return min(float(a['price']) for a in book.asks)

async def run():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    brackets = 0
    detector_opps = 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            detector_opps += 1
        if yb and nb and yb.asks and nb.asks:
            ya, na = best_ask(yb), best_ask(nb)
            s = round(ya + na, 4)
            if s < 1.0:
                brackets += 1
            rows.append({'sum': s, 'q': m.question, 'yes': ya, 'no': na, 'liq': m.liquidity})
    rows.sort(key=lambda r: (r['sum'], -r['liq']))
    band = [r for r in rows if r['sum'] <= 1.005]
    out = {
        'run': TS, 'ts': TS_ISO, 'markets': len(markets), 'priced': len(rows),
        'floor': rows[0]['sum'] if rows else None,
        'brackets_minask': brackets, 'detector_opps': detector_opps,
        'band': len(band), 'top8': rows[:8], 'band_rows': band,
        'scan_time_s': round(scan_time, 1),
    }
    path = f'runs/scan_{TS}.json'
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    shutil.copy(path, 'runs/scan_latest.json')
    print('WROTE', path)
    print(json.dumps(out['top8'], indent=1))

import os
TS = os.environ['RUN_TS']
TS_ISO = os.environ['RUN_TS_ISO']
asyncio.run(run())
