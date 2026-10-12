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
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np, m.question[:50], yp, np, m.liquidity))
    sums.sort()
    return sums

sums = asyncio.run(scan())
print(f"priced markets: {len(sums)}")
brackets = [s for s in sums if s[0] < 1.0]
print(f"min-ask brackets (sum<1.00): {len(brackets)}")
for s in brackets[:10]:
    print(f"  {s[0]:.4f} | Yes@{s[2]:.3f} No@{s[3]:.3f} | liq={s[4]} | {s[1]}")
print("floor (best 8 min-ask sums):")
for s in sums[:8]:
    print(f"  {s[0]:.4f} | Yes@{s[2]:.3f} No@{s[3]:.3f} | liq={s[4]} | {s[1]}")
