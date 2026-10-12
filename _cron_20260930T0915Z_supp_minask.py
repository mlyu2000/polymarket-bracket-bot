import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
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
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), rows

n, rows = asyncio.run(scan())
print(f"SUPP (true best-ask via min): {n} markets")
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"true sum<1.000: {len(brackets)} | true near-miss 1.000-1.005: {len(near)}")
for t, q, yp, np_, liq in rows[:10]:
    print(f"  {t:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
