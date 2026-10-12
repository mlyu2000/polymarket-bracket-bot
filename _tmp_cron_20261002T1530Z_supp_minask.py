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
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # asks are DESC-sorted in the CLOB book -> best ask = min()
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"]); np_ = float(no_ask["price"])
        rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
brackets = [r for r in rows if r[0] < 1.0]
nml = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"MIN-ASK true brackets (sum<1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets[:8]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
print(f"MIN-ASK near-misses (1.00<sum<=1.005): {len(nml)}")
for t, q, yp, np_, liq in nml[:8]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
print("Best min-ask totals overall:")
for t, q, yp, np_, liq in rows[:8]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
