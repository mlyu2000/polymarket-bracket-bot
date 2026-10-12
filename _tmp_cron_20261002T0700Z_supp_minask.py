import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    brackets = []
    near_minask = []
    floor = None
    priced = 0
    top_sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append({'q': m.question[:60], 'sum': opp.total_cost,
                             'yes': opp.yes_price, 'no': opp.no_price,
                             'edge': opp.net_edge, 'shares': opp.max_shares, 'liq': m.liquidity})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            tot = yp + np
            if floor is None or tot < floor:
                floor = tot
            if tot <= 1.005:
                near_minask.append((tot, m.question[:50], yp, np, m.liquidity))
            top_sums.append((tot, m.question[:50], yp, np, m.liquidity))

    near_minask.sort()
    top_sums.sort()
    print(f"[min-ask supplement] markets={len(markets)} priced={priced} time={scan_time:.1f}s")
    print(f"[min-ask] true brackets(sum<1.00 + detector gates): {len(brackets)}")
    for b in brackets:
        print(f"  BRACKET {b['sum']:.3f} | Yes@{b['yes']:.3f} No@{b['no']:.3f} | {b['q']}")
    print(f"[min-ask] true floor = {floor:.4f}")
    print(f"[min-ask] near-misses (<=1.005): {len(near_minask)}")
    for tot, q, yp, np, liq in near_minask[:10]:
        print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("[min-ask] 5 lowest sums overall:")
    for tot, q, yp, np, liq in top_sums[:5]:
        print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
