import asyncio, logging, json, time
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

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    return len(markets), rows

n, rows = asyncio.run(scan())
print(f"markets={n} priced={len(rows)}")
print("TRUE BEST-ASK BRACKETS (sum<1.000):")
brs = [r for r in rows if r[0] < 1.0]
for s, q, ya, na, liq in brs:
    print(f"  sum={s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print(f"count={len(brs)}")
print("TOP 10 CLOSEST (min-ask sum):")
for s, q, ya, na, liq in rows[:10]:
    print(f"  sum={s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
