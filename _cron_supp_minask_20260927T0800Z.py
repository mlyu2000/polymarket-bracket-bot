import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    sums = []
    det_opps = 0
    for m, (yb, nb) in zip(markets, books):
        if detector.detect(m, yb, nb):
            det_opps += 1
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            sums.append((y + n, m.question[:55], y, n, m.liquidity))
    sums.sort()
    print(f"markets={len(markets)} priced={len(sums)} detector_opps={det_opps}")
    print("TOP8 min-ask sums:")
    for s, q, y, n, liq in sums[:8]:
        print(f"  {s:.3f} | Y@{y:.3f} N@{n:.3f} | liq={liq} | {q}")

asyncio.run(main())
