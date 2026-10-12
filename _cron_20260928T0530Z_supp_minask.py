import asyncio, logging, time
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

    opps = []
    near = []
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
                'liq': m.liquidity,
            })
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                # CORRECT best-ask method: min over asks (asks are DESC-sorted)
                yp = min(float(a['price']) for a in yes_book.asks)
                np_ = min(float(a['price']) for a in no_book.asks)
                total = yp + np_
                if total <= 1.005:
                    near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort(key=lambda t: t[0])
    opps.sort(key=lambda o: o['sum'])
    print(f"[supp min-ask] markets={len(markets)} priced_books={priced} scan={scan_time:.1f}s")
    print(f"[supp] TRUE BRACKETS via detector: {len(opps)}")
    for o in opps:
        print(f"  sum={o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
    print(f"[supp] NEAR-MISSES best-ask sum<=1.005: {len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
