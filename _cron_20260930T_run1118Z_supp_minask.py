# Supplementary: true best-ask (min) floor check — asks are DESC-sorted in
# Polymarket /book, so asks[0] is worst. detector.py uses min(); this mirrors
# that for near-miss reporting so the cron report isn't blind to real floors.
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

    best = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        if total <= 1.005:
            best.append((total, m.question[:50], yp, np, m.liquidity))
    best.sort()
    print(f"Markets priced (min-ask): {priced}/{len(markets)}")
    print(f"Min-ask total<=1.005: {len(best)}")
    for total, q, yp, np, liq in best[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
