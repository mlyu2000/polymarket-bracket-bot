import asyncio, logging, json, time, os
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
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append({'sum': round(yp + np_, 4), 'q': m.question[:60], 'yes': yp, 'no': np_, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    return len(markets), rows, scan_time

n_markets, rows, scan_time = asyncio.run(scan())
ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
band = [r for r in rows if r['sum'] <= 1.005]
out = {
    'run': ts,
    'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'markets': n_markets,
    'priced': len(rows),
    'floor': rows[0]['sum'] if rows else None,
    'brackets_minask': sum(1 for r in rows if r['sum'] < 1.0),
    'band': len(band),
    'top8': rows[:8],
    'scan_time_s': round(scan_time, 1),
}
with open(f'runs/scan_{ts}.json', 'w') as f:
    json.dump(out, f, indent=1)
with open('runs/scan_latest.json', 'w') as f:
    json.dump(out, f, indent=1)
# floor tracker
floor_path = 'runs/scan_latest_floor.json'
prev = None
if os.path.exists(floor_path):
    with open(floor_path) as f:
        prev = json.load(f)
with open(floor_path, 'w') as f:
    json.dump({'run': ts, 'floor': out['floor'], 'market': rows[0]['q'] if rows else None,
               'yes': rows[0]['yes'] if rows else None, 'no': rows[0]['no'] if rows else None,
               'liq': rows[0]['liq'] if rows else None,
               'prev_floor': prev.get('floor') if prev else None,
               'prev_run': prev.get('run') if prev else None}, f, indent=1)
print(json.dumps(out, indent=1))
