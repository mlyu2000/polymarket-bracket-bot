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

    brackets = []
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        # asks are DESC-sorted in /book; best ask = min price
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total < 1.0:
            brackets.append((total, yp, np, m.question[:60], m.liquidity))
        elif total <= 1.005:
            near.append((total, yp, np, m.question[:60], m.liquidity))

    brackets.sort()
    near.sort()
    return len(markets), priced, brackets, near

markets_n, priced_n, brackets, near = asyncio.run(scan())
print(f"[min-ask supplement] markets={markets_n} priced={priced_n}")
print(f"[min-ask] true brackets (sum<1.00): {len(brackets)}")
for total, yp, np, q, liq in brackets[:10]:
    print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"[min-ask] near-misses (<=1.005): {len(near)}")
for total, yp, np, q, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
