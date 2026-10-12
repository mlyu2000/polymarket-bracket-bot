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
    near_misses = []   # verbatim method: asks[0]
    best = []          # corrected: min(all asks)
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

        if yes_book and no_book and yes_book.asks and no_book.asks:
            ym = min(float(a['price']) for a in yes_book.asks)
            nm = min(float(a['price']) for a in no_book.asks)
            best.append((ym + nm, m.question[:80], ym, nm, m.liquidity))

    near_misses.sort()
    best.sort()

    # structural stats on books
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        y_asks = bool(yb and yb.asks)
        n_asks = bool(nb and nb.asks)
        if y_asks and n_asks: two_sided += 1
        elif y_asks: yes_only += 1
        elif n_asks: no_only += 1
        else: empty += 1

    tiers = {}
    for band in (1.005, 1.010, 1.020, 1.030, 1.050):
        tiers[band] = sum(1 for s, *_ in best if s <= band)

    with open('runs/_tmp_cron_1845Z_supp_data.json', 'w') as f:
        json.dump({'best': best[:60], 'tiers': tiers}, f, indent=1)

    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'best': best,
        'scan_time': scan_time,
        'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'empty': empty,
        'tiers': tiers,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005) [asks[0] artifact]: {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print()
print("--- Corrected min-ask floor ---")
print(f"TRUE brackets (min-ask sum < 1.00): {sum(1 for s,*_ in result['best'] if s < 1.0)}")
print(f"Band ≤1.005 n={result['tiers'][1.005]} ≤1.010 n={result['tiers'][1.010]} ≤1.020 n={result['tiers'][1.020]} ≤1.030 n={result['tiers'][1.030]} ≤1.050 n={result['tiers'][1.050]}")
for s, q, ym, nm, liq in result['best'][:8]:
    print(f"  {s:.4f} | Yes@{ym:.3f} No@{nm:.3f} | liq {liq} | {q}")
print(f"Books: {result['two_sided']} two-sided / {result['yes_only']} yes-only / {result['no_only']} no-only / {result['empty']} empty")
