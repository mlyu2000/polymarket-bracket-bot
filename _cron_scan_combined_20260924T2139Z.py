# Combined cron scan 20260924T213945Z: detector (min-ask) + provided-script asks[0] near-miss view + best-ask near-miss view.
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

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_asks0 = []
    near_best = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append([opp.total_cost, opp.net_edge, opp.max_shares, m.question[:50], opp.yes_price, opp.no_price, m.liquidity])
            paper.execute(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            a0y = float(yes_book.asks[0]['price']); a0n = float(no_book.asks[0]['price'])
            if a0y + a0n <= 1.005:
                near_asks0.append([round(a0y + a0n, 4), m.question[:50], a0y, a0n, m.liquidity])
            by = min(float(a['price']) for a in yes_book.asks)
            bn = min(float(a['price']) for a in no_book.asks)
            priced += 1
            if by + bn <= 1.005:
                near_best.append([round(by + bn, 4), m.question[:50], by, bn, m.liquidity])

    opps.sort(); near_asks0.sort(); near_best.sort()
    return {
        'ts': '2026-09-24T2139Z',
        'markets': len(markets),
        'priced': priced,
        'scan_time_s': round(scan_time, 1),
        'brackets': opps,
        'near_misses_asks0': near_asks0,
        'near_misses_bestask': near_best,
    }

r = asyncio.run(scan())
with open('runs/cron_scan_20260924T2139Z.json', 'w') as f:
    json.dump(r, f, indent=1)
floor = min((x[0] for x in r['near_misses_bestask']), default=None)
print(f"markets={r['markets']} priced={r['priced']} time={r['scan_time_s']}s brackets={len(r['brackets'])} near_asks0={len(r['near_misses_asks0'])} near_best={len(r['near_misses_bestask'])} floor={floor}")
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(r) + '\n')
