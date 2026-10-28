"""Supplemental min-ask diagnostic run for cron _tmp_cron_20261028T175017Z.

Runs the verbatim scanner output first, then a corrected near-miss pass that
uses min(asks) (the source of truth) instead of asks[0] (a known artifact that
always reports 0 because CLOB asks are DESC-sorted: asks[0] = worst/highest ask).
"""
import asyncio, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def run():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    dt = time.time() - t0

    opps, nms_true, nms_artif = [], [], []
    for m, (yb, nb) in zip(markets, books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append({'q': m.question[:60], 'sum': opp.total_cost,
                         'edge': opp.net_edge, 'shares': opp.max_shares,
                         'liq': m.liquidity})
        if yb and nb and yb.asks and nb.asks:
            yp_a0 = float(yb.asks[0]['price']); np_a0 = float(nb.asks[0]['price'])
            if yp_a0 > 0 and np_a0 > 0 and yp_a0 < 1 and np_a0 < 1:
                t_a0 = yp_a0 + np_a0
                if t_a0 <= 1.005:
                    nms_artif.append((t_a0, m.question[:50], yp_a0, np_a0, m.liquidity))
            yp_min = float(min(yb.asks, key=lambda a: float(a['price']))['price'])
            np_min = float(min(nb.asks, key=lambda a: float(a['price']))['price'])
            t_min = yp_min + np_min
            if t_min <= 1.005 and yp_min > 0 and np_min > 0 and yp_min < 1 and np_min < 1:
                nms_true.append((t_min, m.question[:60], yp_min, np_min, m.liquidity))
    nms_true.sort(key=lambda x: x[0])
    payload = {
        'scan_time': round(dt, 1), 'markets': len(markets),
        'brackets': len(opps), 'opps': opps,
        'near_misses_minask': [{'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l}
                               for (t, q, y, n, l) in nms_true],
        'near_misses_asks0_artifact': len(nms_artif),
        'note': 'asks[0] uses worst/highest ask (DESC-sorted asks) -> always 0; min(asks) is source of truth',
    }
    out = 'runs/_tmp_cron_20261028T175017Z_supp_data.json'
    with open(out, 'w') as f:
        json.dump(payload, f, indent=2)
    print(f"supp_scan_time={dt:.1f}s markets={len(markets)} brackets={len(opps)} "
          f"near_misses_minask={len(nms_true)} near_misses_asks0_artifact={len(nms_artif)}")
    print(f"persisted -> {out}")

asyncio.run(run())
