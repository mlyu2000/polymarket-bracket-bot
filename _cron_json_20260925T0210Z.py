import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    det = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    st = time.time() - t0
    opps, nm_min = [], []
    priced = 0; floor = None
    for m, (yb, nb) in zip(markets, books):
        o = det.detect(m, yb, nb)
        if o:
            opps.append({'sum': o.total_cost, 'edge': o.net_edge, 'yes': o.yes_price, 'no': o.no_price, 'shares': o.max_shares, 'q': m.question[:60], 'liq': m.liquidity})
        elif yb and nb and yb.asks and nb.asks:
            priced += 1
            ym = min(float(a['price']) for a in yb.asks)
            nm = min(float(a['price']) for a in nb.asks)
            tm = ym + nm
            if floor is None or tm < floor: floor = tm
            if tm <= 1.005: nm_min.append([round(tm,3), m.question[:50], ym, nm, m.liquidity])
    nm_min.sort()
    return {'ts': '2026-09-25T0210Z', 'markets': len(markets), 'priced': priced, 'scan_time_s': round(st,1), 'brackets': opps, 'best_floor': ([floor]+nm_min[0][1:]) if nm_min else None, 'near_misses_bestask': nm_min}

print(json.dumps(asyncio.run(scan())))
