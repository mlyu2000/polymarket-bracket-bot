import asyncio, logging, json, time
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
    le102 = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        ymin = min(float(a['price']) for a in yb.asks)
        nmin = min(float(a['price']) for a in nb.asks)
        total = ymin + nmin
        rows.append((total, m.question[:55], ymin, nmin, m.liquidity))
        if total <= 1.02:
            le102.append({
                'q': m.question[:90],
                'yes_min': ymin, 'no_min': nmin, 'sum': round(total, 4),
                'liq': m.liquidity, 'market_id': getattr(m, 'market_id', None) or getattr(m, 'id', None),
                'yes_asks': [{'price': a['price'], 'size': a.get('size')} for a in yb.asks[:3]],
                'no_asks': [{'price': a['price'], 'size': a.get('size')} for a in nb.asks[:3]],
            })
    rows.sort()
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = {
        'ts': ts, 'markets': len(markets), 'scan_time': round(scan_time, 1),
        'floor': [round(rows[0][0],4), rows[0][1], rows[0][2], rows[0][3], rows[0][4]] if rows else None,
        'top10': [{'sum': round(r[0],4), 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]} for r in rows[:10]],
        'tiers': {
            'le_1_005': sum(1 for r in rows if r[0] <= 1.005),
            'le_1_010': sum(1 for r in rows if r[0] <= 1.010),
            'le_1_020': sum(1 for r in rows if r[0] <= 1.020),
            'le_1_050': sum(1 for r in rows if r[0] <= 1.050),
            'lt_1_000': sum(1 for r in rows if r[0] < 1.000),
        },
        'le_1_02_markets': le102,
    }
    with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))

asyncio.run(scan())
