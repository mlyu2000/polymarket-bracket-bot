import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not getattr(book, 'asks', None):
        return None
    return min(book.asks, key=lambda a: float(a['price']))

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya, na = best_ask(yb), best_ask(nb)
        if not ya or not na:
            continue
        priced += 1
        total = float(ya['price']) + float(na['price'])
        near.append((total, m.question[:50], float(ya['price']), float(na['price']), m.liquidity))
    near.sort()
    return markets and len(markets), priced, near

n, priced, near = asyncio.run(scan())
print(f"[MIN-ASK supplement] markets={n} priced={priced}")
print("Overall floor (best-ask sums, true lowest first):")
for total, q, yp, np_, liq in near[:5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
