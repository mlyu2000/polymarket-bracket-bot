# Corrected near-miss supplement: uses min(best ask) instead of asks[0]
# (asks are DESC-sorted on CLOB /book, so asks[0] is the worst ~0.999 quote)
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

    nm = []
    priced = 0
    best_overall = 9.9
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            priced += 1
            best_overall = min(best_overall, tot)
            if tot <= 1.005:
                nm.append((tot, m.question[:50], yp, np_, m.liquidity))
    nm.sort()
    return len(markets), priced, nm, best_overall

n, priced, nm, best = asyncio.run(scan())
print(f"[supplement] markets={n} priced={priced} true_floor(min-ask sums)={best:.4f}")
print(f"[supplement] near-misses (min-ask sum <= 1.005): {len(nm)}")
for t, q, yp, np_, liq in nm[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
