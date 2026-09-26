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
    near_misses = []      # prompt-verbatim: asks[0] (worst ask - DESC-sorted, undercounts)
    best_misses = []      # supplement: min ask (true best price)
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
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                y0 = float(yes_book.asks[0]['price'])
                n0 = float(no_book.asks[0]['price'])
                if y0 + n0 <= 1.005:
                    near_misses.append((round(y0 + n0, 4), m.question[:50], y0, n0, m.liquidity))
                yb = min(float(a['price']) for a in yes_book.asks)
                nb = min(float(a['price']) for a in no_book.asks)
                if m.liquidity > 0 and yb + nb <= 1.005:
                    best_misses.append((round(yb + nb, 4), m.question[:50], yb, nb, m.liquidity))

    near_misses.sort()
    best_misses.sort()
    opps.sort(key=lambda o: o['sum'])
    return {
        'ts': '2026-09-26T0735Z',
        'markets': len(markets),
        'priced': priced,
        'scan_time': scan_time,
        'opps': opps,
        'near_misses_asks0': near_misses,
        'near_misses_bestask': best_misses,
        'best_floor': (best_misses[0] if best_misses else None),
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s (priced={result['priced']})")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  {o['sum']:.3f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
print(f"Near-misses prompt-verbatim asks[0] (<=1.005): {len(result['near_misses_asks0'])}")
for t, q, yp, np_, liq in result['near_misses_asks0'][:5]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"Near-misses best-ask supplement (<=1.005, liq>0): {len(result['near_misses_bestask'])}")
for t, q, yp, np_, liq in result['near_misses_bestask'][:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

with open('runs/cron_scan_2026-09-26T0735Z.json', 'w') as f:
    json.dump(result, f)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(result) + '\n')
