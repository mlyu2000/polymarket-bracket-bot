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
    priced = 0
    true_floors = []
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
                # asks are DESC-sorted in CLOB payload; min() = true best ask
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                priced += 1
                true_floors.append(total)
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    true_floors.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'floor_min': true_floors[0] if true_floors else None,
        'floor_p5': true_floors[max(0, int(len(true_floors)*0.05))] if true_floors else None,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"[minask] markets={result['markets']} priced={result['priced']} in {result['scan_time']:.1f}s")
print(f"[minask] BRACKETS: {len(result['opps'])}")
for o in result['opps']:
    print(f"  {o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']} | {o['q']}")
print(f"[minask] true floor min={result['floor_min']} p5={result['floor_p5']}")
print(f"[minask] near-misses (<=1.005): {len(result['near_misses'])}")
for total, q, yp, npx, liq in result['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npx:.3f} | liq={liq} | {q}")
