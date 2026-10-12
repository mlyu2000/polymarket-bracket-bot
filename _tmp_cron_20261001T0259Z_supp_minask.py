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
    el = time.time() - t0

    rows = []
    brackets = 0
    for m, (yb, nb) in zip(markets, all_books):
        if detector.detect(m, yb, nb):
            brackets += 1
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    print(f"elapsed={el:.1f}s markets={len(markets)} detector_brackets={brackets} priced={len(rows)}")
    print("true floor (min-ask sums), lowest 10:")
    for s, q, yp, np_, liq in rows[:10]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    print(f"count sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")

asyncio.run(scan())
