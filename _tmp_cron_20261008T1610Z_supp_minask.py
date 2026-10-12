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

    opps = []
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                         'sum': opp.total_cost, 'edge': opp.net_edge, 'shares': opp.max_shares, 'liq': m.liquidity})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total <= 1.005:
                near.append((round(total, 4), m.question[:50], yp, np, m.liquidity))

    near.sort()
    print(f"⏱ supp min-ask scan: {len(markets)} markets ({priced} with 2 books) in {scan_time:.1f}s")
    print(f"✅ detector BRACKETS: {len(opps)}")
    for o in opps:
        print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']} | {o['q']}")
    print(f"📊 near-misses (min-ask sum ≤1.005): {len(near)}")
    for t, q, yp, np, liq in near[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if near:
        print(f"FLOOR: {near[0][0]:.3f}")
    with open('_tmp_cron_20261008T1610Z_supp_data.json', 'w') as f:
        json.dump({'near': near, 'opps': opps, 'priced': priced}, f, indent=1)

asyncio.run(scan())
