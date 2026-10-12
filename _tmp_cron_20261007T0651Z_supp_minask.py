import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    brackets = []
    near = []
    priced = 0
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            floors.append(total)
            if 0.995 <= total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    floors.sort()
    return dict(markets=len(markets), priced=priced, dt=dt, brackets=brackets,
                near=near, min_floor=floors[0] if floors else None,
                median=floors[len(floors)//2] if floors else None)

r = asyncio.run(scan())
print(f"markets={r['markets']} priced={r['priced']} time={r['dt']:.1f}s")
print(f"brackets(detector)={len(r['brackets'])}")
for tc, edge, sh, q in sorted(r['brackets']):
    print(f"  BRACKET sum={tc:.4f} edge={edge:.4f} shares={sh} | {q}")
print(f"best-ask floor: min={r['min_floor']:.4f} median={r['median']:.4f}")
print(f"near-misses best-ask (0.995-1.005): {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
