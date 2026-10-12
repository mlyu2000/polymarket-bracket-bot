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
    sums = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            ym = min(float(a['price']) for a in yb.asks)
            nm = min(float(a['price']) for a in nb.asks)
            sums.append((ym+nm, m.question[:55], ym, nm, m.liquidity))
    sums.sort()
    print(f"min-ask pairs scanned: {len(sums)}")
    print("top-8 lowest best-ask sums:")
    for t,q,ym,nm,liq in sums[:8]:
        print(f"  {t:.3f} | Yes@{ym:.3f} No@{nm:.3f} | liq={liq} | {q}")
    print(f"count sum<=1.005: {sum(1 for s in sums if s[0]<=1.005)}")
    print(f"count sum<1.00 (raw, pre-gates): {sum(1 for s in sums if s[0]<1.0)}")

asyncio.run(scan())
