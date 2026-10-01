import asyncio, logging, time, json
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
    near_misses = []
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
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'pairs': list(zip(markets, all_books)),
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  RED {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"Near-misses (<=1.005, verbatim asks[0]): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

# Supplementary: true best-ask (min) floor, matching detector.py logic
print("\n--- SUPPLEMENT: best-ask (min) scan ---")
best_all = []
for m, (yes_book, no_book) in result['pairs']:
    if not m.active or m.closed or m.liquidity <= 0:
        continue
    if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
        continue
    yp = min(float(a['price']) for a in yes_book.asks)
    np_ = min(float(a['price']) for a in no_book.asks)
    if yp <= 0 or np_ <= 0 or yp >= 1.0 or np_ >= 1.0:
        continue
    total = yp + np_
    best_all.append((total, m.question[:60], yp, np_, m.liquidity))
best_all.sort()
print(f"Markets with valid best-ask pair: {len(best_all)}")
print("Floor (5 lowest best-ask sums):")
for total, q, yp, np_, liq in best_all[:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
under1 = [b for b in best_all if b[0] < 1.0]
near = [b for b in best_all if 1.0 <= b[0] <= 1.005]
print(f"Best-ask sums < 1.00: {len(under1)} | in [1.00,1.005]: {len(near)}")
json.dump({'ts': __import__('os').environ.get('BRACKET_TS',''), 'markets': result['markets'], 'scan_time': result['scan_time'], 'opps': result['opps'], 'best_all_top': best_all[:10], 'floor': best_all[0][0] if best_all else None}, open(f'runs/_tmp_cron_{__import__("os").environ.get("BRACKET_TS","")}_data.json','w'))
