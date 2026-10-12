import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            sums.append((ya + na, m.question[:50], ya, na, m.liquidity))
    sums.sort()
    return len(markets), sums

n, sums = asyncio.run(scan())
print(f"TRUE-FLOOR (min asks): {n} markets, priced {len(sums)}")
print(f"brackets sum<1.000: {sum(1 for s in sums if s[0] < 1.0)}")
print(f"near <=1.005: {sum(1 for s in sums if s[0] <= 1.005)}")
for s in sums[:8]:
    print(f"  {s[0]:.4f} | Yes@{s[2]:.3f} No@{s[3]:.3f} | liq={s[4]} | {s[1]}")
