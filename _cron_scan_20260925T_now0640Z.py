# Cron scan 2026-09-25: provided script run verbatim + best-ask (min) near-miss supplement
# matching detector.py logic. Provided script's asks[0] near-miss block is buggy (asks are
# DESC-sorted -> asks[0] is worst ask ~0.999, so it always reports 0 near-misses).
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
    near_misses_firstask = []   # verbatim provided-script logic (asks[0], buggy)
    near_misses_bestask = []    # supplement: min ask, consistent with detector.py
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
            paper.execute(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # verbatim provided logic
            y0 = float(yes_book.asks[0]['price'])
            n0 = float(no_book.asks[0]['price'])
            if y0 + n0 <= 1.005:
                near_misses_firstask.append((y0 + n0, m.question[:50], y0, n0, m.liquidity))
            # best-ask logic
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if total <= 1.005:
                near_misses_bestask.append((round(total, 4), m.question[:50], yp, np_, m.liquidity))

    near_misses_firstask.sort()
    near_misses_bestask.sort()
    opps.sort(key=lambda o: o['sum'])
    return {
        'markets': len(markets),
        'priced': priced,
        'scan_time': scan_time,
        'opps': opps,
        'near_misses_firstask': near_misses_firstask,
        'near_misses_bestask': near_misses_bestask,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  RED sum={o['sum']:.3f} edge={o['edge']:.4f} | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"Near-misses asks[0] verbatim (<=1.005): {len(result['near_misses_firstask'])}")
print(f"Near-misses best-ask supplement (<=1.005): {len(result['near_misses_bestask'])}")
for total, q, yp, np_, liq in result['near_misses_bestask'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

out = {
    'ts': '2026-09-25T_now',
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time_s': round(result['scan_time'], 1),
    'brackets': result['opps'],
    'best_floor': (result['near_misses_bestask'][0] if result['near_misses_bestask'] else None),
    'near_misses_bestask': result['near_misses_bestask'],
}
with open('runs/cron_scan_20260925T_now0640Z.json', 'w') as f:
    json.dump(out, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(out) + '\n')
