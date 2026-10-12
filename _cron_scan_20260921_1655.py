import asyncio, logging, time, json, os
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
    paper_results = []
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
            pr = paper.execute(opp)
            paper_results.append({
                'q': m.question[:60],
                'sum': opp.total_cost,
                'yes_fill': f"{pr.yes_fill.outcome}@{pr.yes_fill.price}:{pr.yes_fill.size}",
                'no_fill': f"{pr.no_fill.outcome}@{pr.no_fill.price}:{pr.no_fill.size}",
                'unhedged': pr.unhedged,
                'pnl': pr.final_pnl,
            })
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # asks[0] is worst ask (CLOB returns asks DESC-sorted);
                # detector uses min(). Report min-ask sums as truth here.
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'paper_results': paper_results,
    }

result = asyncio.run(scan())
ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
result['ts'] = ts
os.makedirs('runs', exist_ok=True)
with open(os.path.join('runs', f'cron_scan_{ts.replace(":", "").replace("-", "")}.json'), 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
for p in result['paper_results']:
    print(f"  📝 PAPER: {p['q']} | Y {p['yes_fill']} | N {p['no_fill']} | unhedged={p['unhedged']} | pnl={p['pnl']}")
print(f"📊 Near-misses (≤1.005, min-ask): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
