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

    # --- mechanism-agnostic min-ask (true best ask) pass, same rule as detector.py ---
    near_misses_min = []
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            floors.append((total, m.question[:50], m.liquidity))
            if 1.000 <= total <= 1.005:
                near_misses_min.append((total, m.question[:50], yp, np_, m.liquidity))

    floors.sort()
    near_misses.sort()
    near_misses_min.sort()
    return {
        'markets': len(markets),
        'priced': len(floors),
        'opps': opps,
        'near_misses': near_misses,
        'near_misses_min': near_misses_min,
        'floors': floors[:10],
        'count_1010': sum(1 for s, _, _ in floors if s <= 1.010),
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  BRACKET {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"Near-misses verbatim asks[0] (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"Near-misses min-ask (1.000<=sum<=1.005): {len(result['near_misses_min'])}")
for total, q, yp, np_, liq in result['near_misses_min'][:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Priced both-sides: {result['priced']} | count<=1.010: {result['count_1010']}")
print("Top-10 lowest best-ask totals:")
for total, q, liq in result['floors'][:10]:
    print(f"  {total:.4f} | liq={liq} | {q}")
