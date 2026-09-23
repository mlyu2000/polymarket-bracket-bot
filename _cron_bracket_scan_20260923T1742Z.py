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
    # Supplementary: corrected min-ask pass (CLOB asks are DESC-sorted; asks[0] = worst)
    true_near = []
    true_brackets = []
    all_sums = []
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
                ym = min(float(a['price']) for a in yes_book.asks)
                nm = min(float(a['price']) for a in no_book.asks)
                tsum = ym + nm
                priced += 1
                all_sums.append((tsum, m.question[:60], m.liquidity))
                if tsum < 1.0:
                    true_brackets.append((tsum, m.question[:60], ym, nm, m.liquidity))
                elif tsum <= 1.005:
                    true_near.append((tsum, m.question[:60], ym, nm, m.liquidity))

    near_misses.sort()
    true_near.sort()
    true_brackets.sort()
    all_sums.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'true_near': true_near,
        'true_brackets': true_brackets,
        'scan_time': scan_time,
        'priced': priced,
        'floor': all_sums[0] if all_sums else None,
        'top5': all_sums[:5],
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  [{o['sum']:.3f} edge={o['edge']:.4f}] Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"Near-misses (asks[0], <=1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
print(f"-- corrected min-ask pass --")
print(f"Priced markets: {result['priced']}")
if result['floor']:
    print(f"Floor sum: {result['floor'][0]:.4f} ({result['floor'][1]})")
print(f"True brackets (min-ask sum<1.00): {len(result['true_brackets'])}")
for total, q, yp, np_, liq in result['true_brackets'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"True near-misses (min-ask <=1.005): {len(result['true_near'])}")
for total, q, yp, np_, liq in result['true_near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
