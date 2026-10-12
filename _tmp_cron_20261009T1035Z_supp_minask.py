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
    near_misses = []
    true_min = (9.0, None)
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity
            })
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(float(a['price']) for a in yes_book.asks)
            no_ask = min(float(a['price']) for a in no_book.asks)
            total = yes_ask + no_ask
            if total < true_min[0]:
                true_min = (total, m.question[:60])
            if total >= 1.0 and total <= 1.005:
                near_misses.append((total, m.question[:50], yes_ask, no_ask, m.liquidity))

    near_misses.sort()
    return markets, opps, near_misses, true_min, scan_time

markets, opps, near_misses, true_min, scan_time = asyncio.run(scan())
priced = [t for t in near_misses]
print(f"🔍 Best-ask scan: {len(markets)} markets in {scan_time:.1f}s")
print(f"✅ BRACKETS (sum < 1.00 via detector): {len(opps)}")
for o in opps:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"📊 Near-misses (1.000 < sum <= 1.005, best asks): {len(near_misses)}")
for total, q, yp, np, liq in near_misses[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"📉 Global min best-ask sum: {true_min[0]:.3f} | {true_min[1]}")
