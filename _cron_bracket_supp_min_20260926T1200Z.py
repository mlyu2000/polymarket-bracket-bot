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
    dt = time.time() - t0

    br, nm, priced = [], [], 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            br.append(opp)
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            priced += 1
            if tot < 1.0:
                br.append(('raw-min', tot, m.question[:60]))
            elif tot <= 1.005:
                nm.append((tot, m.question[:50], yp, np_, m.liquidity))
    nm.sort()
    return br, nm, priced, len(markets), dt

br, nm, priced, n, dt = asyncio.run(scan())
print(f"scan {n} markets in {dt:.1f}s; priced={priced}")
print(f"BRACKETS detector+raw-min: {len(br)}")
for x in br:
    print(' ', x if isinstance(x, tuple) else f"{x.total_cost:.3f} edge={x.net_edge:.4f} {x.yes_price:.3f}/{x.no_price:.3f} {x.max_shares}sh")
print(f"NEAR-MISS min-ask <=1.005: {len(nm)}")
for t, q, yp, np_, liq in nm[:10]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
