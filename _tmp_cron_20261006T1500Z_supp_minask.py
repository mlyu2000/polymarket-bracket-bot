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
    near = []      # best-ask sum in (1.00, 1.005]
    priced = 0
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.liquidity, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            sums.append(total)
            if 1.0 < total <= 1.005 and m.liquidity >= Config.MIN_LIQUIDITY_USDC and m.liquidity > 0:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    sums.sort()
    return dict(markets=len(markets), priced=priced, opps=opps, near=near,
                floor=sums[0] if sums else None,
                p05=sums[max(0, int(len(sums)*0.05))] if sums else None,
                median=sums[len(sums)//2] if sums else None,
                scan_time=scan_time)

r = asyncio.run(scan())
print(f"[supp min-ask] markets={r['markets']} priced_books={r['priced']} in {r['scan_time']:.1f}s")
print(f"[supp] detector brackets: {len(r['opps'])}")
for s, e, sh, liq, q in sorted(r['opps']):
    print(f"  BRACKET sum={s:.3f} net_edge={e:.4f} shares={sh} liq={liq} | {q}")
print(f"[supp] best-ask floor={r['floor']} p05={r['p05']} median={r['median']}")
print(f"[supp] near-misses 1.00<sum<=1.005 (liq-filtered): {len(r['near'])}")
for total, q, yp, npp, liq in r['near'][:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{npp:.3f} | liq={liq} | {q}")
