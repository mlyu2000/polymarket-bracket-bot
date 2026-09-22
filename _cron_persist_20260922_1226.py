"""Single scan: collect min-ask data + detector brackets, persist runs/ JSON (same schema as prior cron runs)."""
import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    near, brackets = [], []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({'q': m.question[:80], 'sum': opp.total_cost,
                             'edge': opp.net_edge, 'shares': opp.max_shares})
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = round(yp + np_, 6)
            priced += 1
            if total <= 1.005:
                near.append({'sum': total, 'q': m.question[:80], 'yes': yp, 'no': np_, 'liq': m.liquidity})
    near.sort(key=lambda r: r['sum'])
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = {'ts': ts, 'method': 'min-ask', 'markets': len(markets), 'priced': priced,
           'scan_seconds': scan_time, 'best_min_sum': near[0]['sum'] if near else None,
           'detector_brackets': brackets, 'brackets': brackets, 'near_le_1005': near}
    path = f'runs/cron_scan_{ts}.json'
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print(f"saved {path}: {len(brackets)} brackets, {len(near)} near-misses, floor={out['best_min_sum']}")

asyncio.run(main())
