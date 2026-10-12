import asyncio, logging, json, time, os
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    def best_ask(book):
        if not book or not book.asks:
            return None
        return min(float(a['price']) for a in book.asks)

    rows = []
    brackets = 0
    detector_opps = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya = best_ask(yes_book)
        na = best_ask(no_book)
        if detector.detect(m, yes_book, no_book):
            detector_opps += 1
        if ya is None or na is None:
            continue
        total = ya + na
        if total < 1.0:
            brackets += 1
        rows.append({'sum': round(total, 4), 'q': m.question[:60], 'yes': ya, 'no': na, 'liq': m.liquidity})

    rows.sort(key=lambda r: r['sum'])
    band = [r for r in rows if 1.0 <= r['sum'] <= 1.005]
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = {
        'run': ts,
        'markets': len(markets),
        'priced': len(rows),
        'floor': rows[0]['sum'] if rows else None,
        'brackets_minask': brackets,
        'detector_opps': detector_opps,
        'band': len(band),
        'band_rows': band,
        'top8': rows[:8],
        'scan_time_s': round(scan_time, 1),
    }
    os.makedirs('runs', exist_ok=True)
    with open(f'runs/scan_{ts}.json', 'w') as f:
        json.dump(out, f, indent=1)
    with open('runs/scan_latest.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))

asyncio.run(scan())
