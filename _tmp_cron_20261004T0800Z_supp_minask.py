import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        s = yp + np
        opp = detector.detect(m, yb, nb)
        rows.append((s, m.question[:55], yp, np, m.liquidity, opp is not None))
    rows.sort()
    return rows, len(markets)

rows, nmarkets = asyncio.run(scan())
under1 = [r for r in rows if r[0] < 1.0]
nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"Markets: {nmarkets} | best-ask sums computed: {len(rows)}")
print(f"TRUE best-ask sum < 1.00: {len(under1)}")
for s, q, yp, np, liq, det in under1[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | det={det} | {q}")
print(f"TRUE best-ask sum in [1.00, 1.005]: {len(nm)}")
for s, q, yp, np, liq, det in nm[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
