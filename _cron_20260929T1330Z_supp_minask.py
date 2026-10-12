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

    opps = []
    near = []
    priced = 0
    best_overall = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if best_overall is None or total < best_overall[0]:
                best_overall = (total, m.question[:60], yp, np_, m.liquidity)
            if total < 1.00:
                near.append((total, m.question[:60], yp, np_, m.liquidity, 'TRUE-BRACKET'))
            elif total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity, 'near'))
    near.sort()
    return markets, opps, near, priced, best_overall, dt

result = asyncio.run(scan())
markets, opps, near, priced, best_overall, dt = result
print(f"min-ask pass: {len(markets)} markets, {priced} with both books, in {dt:.1f}s")
print(f"TRUE BRACKETS (min-ask sum<1.00): {len(opps)}")
for o in opps:
    print(f"  [BRACKET] sum={o.total_cost:.4f} gross={o.gross_edge:.4f} net={o.net_edge:.4f} Yes@{o.yes_price:.3f} No@{o.no_price:.3f} {o.max_shares}sh ${o.max_usdc} | {o.market.question[:60]}")
print(f"Near-misses (min-ask, <=1.005): {len(near)}")
for total, q, yp, np_, liq, tag in near[:10]:
    print(f"  {tag} {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if best_overall:
    total, q, yp, np_, liq = best_overall
    print(f"LOWEST SUM ANYWHERE: {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
