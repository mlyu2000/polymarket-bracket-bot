import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        sums.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    sums.sort()
    print(f"priced markets: {len(sums)} (of {len(markets)})")
    print(f"brackets best-ask sum<1.00: {sum(1 for s in sums if s[0] < 1.0)}")
    print(f"near-misses best-ask sum<=1.005: {sum(1 for s in sums if s[0] <= 1.005)}")
    print("top 8 lowest sums (best-ask):")
    for total, q, yp, np_, liq in sums[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    return sums

asyncio.run(scan())
