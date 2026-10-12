import asyncio, logging, time
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
    near_misses = []      # provided method: asks[0] (known: DESC order -> worst ask)
    best_all = []         # supplement: min-ask totals across all priced markets
    best_opps = []        # supplement: sum<1.00 on best asks
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
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

        # Supplement: best-ask (min price) totals — CLOB /book asks are DESC-sorted
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            t = yp + np_
            priced += 1
            best_all.append((t, m.question[:50], yp, np_, m.liquidity, 'live' if (m.active and not m.closed and m.liquidity > 0) else 'guard'))
            if t < 1.00 and m.active and not m.closed and m.liquidity > 0:
                best_opps.append((t, m.question[:60], yp, np_, m.liquidity))

    near_misses.sort()
    best_all.sort()
    best_opps.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': priced,
        'best_all': best_all,
        'best_opps': best_opps,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS via detector (min-ask, guards, edge>=margin): {len(result['opps'])}")
for o in result['opps']:
    print(f"  OPP sum={o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
print(f"Near-misses per prompt asks[0] logic (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"--- Supplement (best-ask min; {result['priced']} priced pairs) ---")
print(f"sum<1.00 on best asks (active/liq>0): {len(result['best_opps'])}")
for t, q, yp, np_, liq in result['best_opps'][:10]:
    print(f"  BRACKET sum={t:.4f} Yes@{yp:.3f} No@{np_:.3f} liq={liq} | {q}")
print(f"Top-10 lowest best-ask totals (all priced):")
for t, q, yp, np_, liq, g in result['best_all'][:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} liq={liq} [{g}] | {q}")
