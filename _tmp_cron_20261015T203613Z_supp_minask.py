import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    frozen = {}
    for m, (yb, nb) in zip(markets, all_books):
        y = best_ask(yb); n = best_ask(nb)
        if y is None or n is None:
            continue
        rows.append((y + n, m.question[:55], y, n, m.liquidity))
        # raw book fingerprint for frozen-book detection
        fp = json.dumps({'y': sorted((float(a['price']), float(a['size'])) for a in (yb.asks if yb else [])),
                         'n': sorted((float(a['price']), float(a['size'])) for a in (nb.asks if nb else []))})
        frozen[m.question[:55]] = (hash(fp), y + n)
    rows.sort()

    tiers = {'le1.000': 0, 'le1.005': 0, 'le1.010': 0, 'le1.020': 0, 'le1.050': 0, 'lt1.000': 0}
    for total, *_ in rows:
        if total < 1.000: tiers['lt1.000'] += 1
        if total <= 1.000: tiers['le1.000'] += 1
        if total <= 1.005: tiers['le1.005'] += 1
        if total <= 1.010: tiers['le1.010'] += 1
        if total <= 1.020: tiers['le1.020'] += 1
        if total <= 1.050: tiers['le1.050'] += 1

    out = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'two_sided': len(rows),
        'scan_time': round(scan_time, 1),
        'floor': round(rows[0][0], 4) if rows else None,
        'top5': [(round(r[0],4), r[1], r[2], r[3], r[4]) for r in rows[:5]],
        'tiers': tiers,
        'frozen': frozen,
    }
    with open('runs/_tmp_cron_20261015T203613Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != 'frozen'}, indent=2))

asyncio.run(scan())
