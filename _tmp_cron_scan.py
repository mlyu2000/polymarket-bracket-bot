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
    both_asks = 0
    yes_only = 0
    # true min-ask floor across all markets (uses min(all asks), not asks[0])
    floor_candidates = []
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
                both_asks += 1
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                # true floor: min ask on each side
                ymin = min(float(a['price']) for a in yes_book.asks)
                nmin = min(float(a['price']) for a in no_book.asks)
                floor_candidates.append((ymin + nmin, m.question[:60], ymin, nmin, m.liquidity))
            else:
                yes_only += 1

    near_misses.sort()
    floor_candidates.sort()
    # liquidity-weighted top near-miss candidates
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'both_asks': both_asks,
        'yes_only': yes_only,
        'floor_top': floor_candidates[:8],
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (asks[0], ≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"📐 True min-ask floor (both-asks n={result['both_asks']}, yes-only/unbracketable n={result['yes_only']}):")
for total, q, yp, np, liq in result['floor_top']:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq {liq} | {q}")
with open('runs/_tmp_cron_supp_data.json', 'w') as f:
    json.dump(result, f, indent=1, default=str)
print("persisted: runs/_tmp_cron_supp_data.json")
