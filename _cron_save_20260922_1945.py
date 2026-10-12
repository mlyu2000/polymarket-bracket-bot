import json, asyncio, time, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    brackets = []
    near = []
    priced = 0
    best = None
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({'sum': opp.total_cost, 'edge': opp.net_edge, 'shares': opp.max_shares,
                             'q': m.question, 'yes': opp.yes_price, 'no': opp.no_price, 'liq': m.liquidity})
        elif yb and nb and yb.asks and nb.asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            s = yp + np_
            if best is None or s < best:
                best = s
            if s <= 1.005:
                near.append({'sum': s, 'q': m.question, 'yes': yp, 'no': np_, 'liq': m.liquidity})
    near.sort(key=lambda x: x['sum'])
    out = {
        'ts': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()),
        'method': 'min-ask',
        'markets': len(markets),
        'priced': priced,
        'scan_seconds': scan_time,
        'best_min_sum': best,
        'brackets': brackets,
        'near_le_1005': near,
    }
    path = f"runs/cron_scan_{out['ts']}.json"
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print(path)

asyncio.run(main())
