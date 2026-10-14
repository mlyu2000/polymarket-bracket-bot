import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    det = BracketDetector()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    t0 = time.time()
    books = await api.fetch_order_books_batch(pairs)
    dt = time.time() - t0

    opps, near, two_sided, yes_only, empty = [], [], 0, 0, 0
    bands = {b: 0 for b in (1.000, 1.005, 1.010, 1.020, 1.030)}
    sums = []
    for m, (yb, nb) in zip(markets, books):
        opp = det.detect(m, yb, nb)
        if opp:
            opps.append({'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                         'sum': opp.total_cost, 'edge': opp.net_edge, 'shares': opp.max_shares,
                         'liq': m.liquidity})
            continue
        if yb and nb and yb.asks and nb.asks:
            two_sided += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            t = yp + np_
            sums.append(t)
            for b in bands:
                if t <= b:
                    bands[b] += 1
            if t <= 1.010:
                near.append({'sum': t, 'q': m.question[:60], 'yes': yp, 'no': np_, 'liq': m.liquidity})
        elif (yb and yb.asks) and not (nb and nb.asks):
            yes_only += 1
        else:
            empty += 1

    sums.sort()
    med = sums[len(sums)//2] if sums else None
    data = {'ts': '20261014T021455Z', 'markets': len(markets), 'scan_time': round(dt, 1),
            'brackets': opps, 'true_near_misses_le_1.010': near, 'counts': {
                'two_sided': two_sided, 'yes_only': yes_only, 'empty': empty},
            'bands': {str(k): v for k, v in bands.items()}, 'median_sum': med,
            'floor': sums[0] if sums else None, 'floor_market': near[0] if near else None}
    with open('runs/_tmp_cron_20261014T021455Z_supp_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(json.dumps({'brackets': len(opps), 'floor': sums[0] if sums else None,
                      'two_sided': two_sided, 'yes_only': yes_only, 'empty': empty,
                      'bands': data['bands'], 'median': med, 'scan_time': round(dt, 1)}, indent=2))

asyncio.run(scan())
