import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not getattr(book, 'asks', None):
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets = []
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        y = best_ask(yes_book)
        n = best_ask(no_book)
        if y is None or n is None:
            continue
        priced += 1
        total = y + n
        if total < 1.00:
            brackets.append((total, m.question[:60], y, n, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], y, n, m.liquidity))

    brackets.sort()
    near.sort()
    return markets, priced, brackets, near

result = asyncio.run(scan())
markets, priced, brackets, near = result
print(f"[BEST-ASK] markets={len(markets)} priced={priced}")
print(f"[BEST-ASK] true brackets sum<1.00: {len(brackets)}")
for total, q, y, n, liq in brackets[:10]:
    print(f"  {total:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
print(f"[BEST-ASK] near-misses 1.00<sum<=1.005: {len(near)}")
for total, q, y, n, liq in near[:5]:
    print(f"  {total:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
