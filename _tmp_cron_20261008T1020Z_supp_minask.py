import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    return min(float(a['price']) for a in book.asks)

async def run():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    brackets = 0
    for m, (yb, nb) in zip(markets, all_books):
        if detector.detect(m, yb, nb):
            brackets += 1
        if yb and nb and yb.asks and nb.asks:
            ya, na = best_ask(yb), best_ask(nb)
            rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    priced = len(rows)
    print(f"markets={len(markets)} priced_pairs={priced} detector_brackets={brackets}")
    if rows:
        print(f"true_floor_sum={rows[0][0]:.4f}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near_misses_bestask(<=1.005)={len(nm)}")
    for total, q, ya, na, liq in nm[:10]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(run())
