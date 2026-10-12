import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
            no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
            yp, np = float(yes_ask["price"]), float(no_ask["price"])
            sums.append((yp + np, m.question[:60], yp, np, m.liquidity))
    sums.sort()
    return sums

sums = asyncio.run(scan())
print(f"min-ask sums computed for {len(sums)} markets")
print("lowest 8:")
for total, q, yp, np, liq in sums[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
brackets = [s for s in sums if s[0] < 1.00]
print(f"true brackets (min-ask sum < 1.00): {len(brackets)}")
for total, q, yp, np, liq in brackets:
    print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
