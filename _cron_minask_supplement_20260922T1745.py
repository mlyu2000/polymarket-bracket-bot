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
    corrected_near = []
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
                cy = min(float(a['price']) for a in yes_book.asks)
                cn = min(float(a['price']) for a in no_book.asks)
                corrected_near.append((cy + cn, m.question[:50], cy, cn, m.liquidity))

    corrected_near.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'corrected_near': corrected_near[:8],
        'corrected_count': sum(1 for t, *_ in corrected_near if t <= 1.005),
        'floor': corrected_near[0][0] if corrected_near else None,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Markets: {result['markets']}  Priced: {result['priced']}  Time: {result['scan_time']:.1f}s")
print(f"BRACKETS (true best-ask sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 sum={o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']} | {o['q']}")
print(f"True best-ask floor: {result['floor']:.4f}" if result['floor'] else "no priced markets")
print(f"Count <=1.005: {result['corrected_count']}")
for total, q, yp, np, liq in result['corrected_near']:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
