import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()
    ts = open('/tmp/ts.txt').read().strip()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_asks0 = []
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                         'sum': opp.total_cost, 'edge': opp.net_edge,
                         'shares': opp.max_shares, 'liq': m.liquidity})
            paper.execute(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            a0y = float(yes_book.asks[0]['price']); a0n = float(no_book.asks[0]['price'])
            if a0y + a0n <= 1.005:
                near_asks0.append({'sum': round(a0y+a0n,4), 'q': m.question[:50], 'yes': a0y, 'no': a0n, 'liq': m.liquidity})
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            priced += 1
            rows.append({'sum': round(ya+na,4), 'q': m.question[:60], 'yes': ya, 'no': na, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    near_min = [r for r in rows if 1.0 <= r['sum'] <= 1.005]
    under = [r for r in rows if r['sum'] < 1.0]
    out = {
        'ts': ts, 'method': 'provided(asks[0]) + detector + minask floor',
        'markets': len(markets), 'priced': priced, 'scan_seconds': round(scan_time,2),
        'best_min_sum': rows[0]['sum'] if rows else None,
        'brackets': opps,
        'sub1_minask': under,
        'near_le_1005_provided_asks0': sorted(near_asks0, key=lambda r: r['sum']),
        'near_le_1005_minask': near_min,
        'near_le_1005_minask_count': len(near_min),
    }
    path = f'runs/cron_scan_{ts}.json'
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print(f"saved {path}")
    print(f"markets={len(markets)} priced={priced} scan={scan_time:.1f}s")
    print(f"brackets={len(opps)} sub1_minask={len(under)} near_minask={len(near_min)} near_asks0={len(near_asks0)}")

asyncio.run(scan())
