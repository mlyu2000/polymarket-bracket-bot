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
    best_near = []
    priced = 0
    floor = 2.0
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
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                floor = min(floor, total)
                if total <= 1.005:
                    best_near.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    best_near.sort()
    print(f"BEST-ASK SCAN: {len(markets)} markets ({priced} priced) in {scan_time:.1f}s")
    print(f"BRACKETS (detector, sum<1.00): {len(opps)}")
    for o in opps:
        print(f"  RED sum={o['sum']:.3f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']} | {o['q']}")
    print(f"Best-ask floor across priced markets: {floor:.3f}")
    print(f"BEST-ASK NEAR-MISSES (<=1.005): {len(best_near)}")
    for total, q, yp, np, liq in best_near[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
