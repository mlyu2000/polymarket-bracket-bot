import asyncio, json, logging, time
from datetime import datetime, timezone
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

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_min = []
    verbatim_nm = 0
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity
            })
            paper.execute(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            y0 = float(yes_book.asks[0]['price']); n0 = float(no_book.asks[0]['price'])
            if y0 + n0 <= 1.005:
                verbatim_nm += 1
            ym = min(float(a['price']) for a in yes_book.asks)
            nm = min(float(a['price']) for a in no_book.asks)
            total = ym + nm
            if total <= 1.005:
                near_min.append([round(total, 4), m.question[:60], ym, nm, m.liquidity])
    near_min.sort()
    return {
        'markets': len(markets), 'priced': priced,
        'opps': opps, 'near_min': near_min,
        'verbatim_nm': verbatim_nm,
        'floor': (near_min[0][0] if near_min else None),
        'scan_time': scan_time,
    }

r = asyncio.run(scan())
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%MZ')
iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')

hist = {
    'stamp': stamp, 'markets': r['markets'], 'priced': r['priced'],
    'floor': r['near_min'][0][0] if r['near_min'] else None,
    'brackets': r['opps'],
    'near_misses': r['near_min'],
    'verbatim_near_misses_asks0': r['verbatim_nm'],
    'note': 'verbatim asks[0] near-miss counts DESC-sorted worst ask (known artifact); min-ask best-ask scan authoritative',
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(hist) + '\n')

latest = {
    'ts_utc': iso,
    'scan_verbatim': {
        'markets': r['markets'], 'scan_time_s': round(r['scan_time'], 1),
        'brackets': len(r['opps']), 'near_misses_asks0': r['verbatim_nm'],
    },
    'supp_bestask': {
        'priced': r['priced'],
        'true_floor': r['near_min'][0][0] if r['near_min'] else None,
        'sums_le_1.005': [
            {'sum': s, 'yes': y, 'no': n, 'liq': liq, 'q': q}
            for s, q, y, n, liq in r['near_min']
        ],
    },
    'paper_trades_executed': len(r['opps']),
    'scan': stamp,
}
with open('runs/scan_latest.json', 'w') as f:
    json.dump(latest, f, indent=2)

print(f"PERSISTED stamp={stamp} brackets={len(r['opps'])} near_min={len(r['near_min'])} floor={latest['supp_bestask']['true_floor']}")
