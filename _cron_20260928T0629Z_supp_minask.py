import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total < 1.00:
            brackets.append((total, m.question[:60], yp, np, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], yp, np, m.liquidity))
    brackets.sort()
    near.sort()
    return markets, brackets, near

markets, brackets, near = asyncio.run(scan())
print(f"BEST-ASK SCAN ({len(markets)} markets)")
print(f"brackets_best_ask={len(brackets)}  near_miss_best_ask={len(near)}")
for total, q, yp, np, liq in brackets[:10]:
    print(f"  BRACKET {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
for total, q, yp, np, liq in near[:10]:
    print(f"  NEAR {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
