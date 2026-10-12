# Supplementary: correct near-miss measure using min ask (detector-consistent),
# since asks are DESC-sorted and asks[0] is the worst ask.
import asyncio, logging, time
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

    near = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if detector.detect(m, yb, nb):
            continue  # already a bracket
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            if yp > 0 and np_ > 0 and yp < 1.0 and np_ < 1.0:
                priced += 1
                total = yp + np_
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    return priced, near

priced, near = asyncio.run(scan())
print(f"Markets with valid min-ask pricing: {priced}")
print("TRUE best min-ask sums (top 10):")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Count sum<=1.00: {sum(1 for t,*_ in near if t<=1.0)}")
print(f"Count sum<=1.005: {sum(1 for t,*_ in near if t<=1.005)}")
