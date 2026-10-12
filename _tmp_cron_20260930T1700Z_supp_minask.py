import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # CLOB /book returns asks DESC-sorted; best ask = min price
        yes_ask = min(float(a['price']) for a in yes_book.asks)
        no_ask = min(float(a['price']) for a in no_book.asks)
        total = yes_ask + no_ask
        sums.append((total, m.question[:55], yes_ask, no_ask, m.liquidity))
        if total < 1.0:
            brackets.append((total, m.question[:60], yes_ask, no_ask, m.liquidity))

    sums.sort()
    return sums, brackets

sums, brackets = asyncio.run(scan())
print(f"Markets priced: {len(sums)}")
print(f"BRACKETS via best(min) ask, sum<1.00: {len(brackets)}")
for t, q, y, n, liq in brackets:
    print(f"  *** {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
print("Top-8 lowest sums (best-ask method):")
for t, q, y, n, liq in sums[:8]:
    flag = "<=1.005" if t <= 1.005 else ""
    print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | {flag} | {q}")
