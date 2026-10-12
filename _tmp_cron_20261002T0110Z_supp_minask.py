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

    priced = 0
    best = []   # (sum, q, yp, np, liq) using best asks = min(price)
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            best.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    best.sort()
    return len(markets), priced, best

n, priced, best = asyncio.run(scan())
print(f"markets={n} priced_books={priced}")
print("--- top 10 lowest YES+NO best-ask sums ---")
for s, q, yp, np_, liq in best[:10]:
    tag = "BRACKET" if s < 1.0 else ("near" if s <= 1.005 else "")
    print(f"  sum={s:.3f} {tag} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"count(sum<=1.00)={sum(1 for b in best if b[0] <= 1.0)}")
print(f"count(sum<=1.005)={sum(1 for b in best if b[0] <= 1.005)}")
print(f"count(sum<=1.01)={sum(1 for b in best if b[0] <= 1.01)}")
