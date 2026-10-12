import asyncio, json, logging, time
from datetime import datetime, timezone
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
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        y_asks = [float(a['price']) for a in (yb.asks if yb else [])]
        n_asks = [float(a['price']) for a in (nb.asks if nb else [])]
        if y_asks and n_asks:
            two_sided += 1
            total = min(y_asks) + min(n_asks)
            rows.append((total, m.question[:60], min(y_asks), min(n_asks), m.liquidity))
        elif y_asks and not n_asks:
            yes_only += 1
        elif n_asks and not y_asks:
            no_only += 1
        else:
            empty += 1

    rows.sort()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    tiers = {
        'le1000': sum(1 for r in rows if r[0] <= 1.000),
        'le1005': sum(1 for r in rows if r[0] <= 1.005),
        'le1010': sum(1 for r in rows if r[0] <= 1.010),
        'le1020': sum(1 for r in rows if r[0] <= 1.020),
        'le1030': sum(1 for r in rows if r[0] <= 1.030),
    }
    out = {
        'ts': ts,
        'markets': len(markets),
        'scan_time': round(scan_time, 1),
        'tiers': tiers,
        'structural': {'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'empty': empty},
        'top10': [
            {'total': round(r[0], 4), 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]}
            for r in rows[:10]
        ],
    }
    with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

asyncio.run(scan())
