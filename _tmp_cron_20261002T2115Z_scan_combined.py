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

    def best_ask(book):
        # CLOB asks are DESC-sorted; asks[0] is the WORST ask.
        return min(float(a['price']) for a in book.asks)

    opps = []
    near_misses = []       # verbatim prompt version (asks[0]) — known artifact
    near_misses_min = []   # corrected: best ask via min()
    floors = []
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
                yb = best_ask(yes_book)
                nb = best_ask(no_book)
                tmin = yb + nb
                floors.append((tmin, m.question[:50], yb, nb, m.liquidity))
                if tmin <= 1.005:
                    near_misses_min.append((tmin, m.question[:50], yb, nb, m.liquidity))

    near_misses.sort()
    near_misses_min.sort()
    floors.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'near_misses_min': near_misses_min,
        'floor': floors[0] if floors else None,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  >> {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"Near-misses (<=1.005, verbatim asks[0]): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"Near-misses (<=1.005, corrected min-ask): {len(result['near_misses_min'])}")
for total, q, yp, np_, liq in result['near_misses_min'][:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if result['floor']:
    f = result['floor']
    print(f"Floor (min-ask sum): {f[0]:.4f} | Yes@{f[2]:.3f} No@{f[3]:.3f} | liq={f[4]} | {f[1]}")
with open('_tmp_cron_20261002T2115Z_scan_data.json', 'w') as fh:
    json.dump(result, fh, default=str)
