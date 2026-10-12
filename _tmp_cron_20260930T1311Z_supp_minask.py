import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if total < 1.00:
            brackets += 1
        if total <= 1.005:
            rows.append((total, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    floor = rows[0][0] if rows else None
    print(f"[supp min-ask] {len(markets)} markets ({priced} priced) in {dt:.1f}s")
    print(f"[supp min-ask] BRACKETS (sum<1.00): {brackets}")
    print(f"[supp min-ask] Near-misses (sum<=1.005): {len(rows)}")
    for total, q, yp, np_, liq in rows[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

    import json, datetime
    rec = {
        'scan_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'markets': len(markets),
        'scan_time_s': round(dt, 1),
        'brackets_true_minask': brackets,
        'near_misses_true_minask': len(rows),
        'best_ask_floor': floor,
        'priced_markets': priced,
        'top_true_sums': [
            {'sum': t, 'yes': y, 'no': n, 'liq': round(l, 0), 'q': q}
            for t, q, y, n, l in rows[:8]
        ],
    }
    with open('/tmp/supp_record_1311.json', 'w') as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
    print('[supp] record written to /tmp/supp_record_1311.json')

asyncio.run(supp())
