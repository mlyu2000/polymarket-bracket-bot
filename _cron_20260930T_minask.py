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

    near = []
    under1 = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        if m.liquidity > 0:
            if total < 1.0:
                under1.append((total, m.question[:60], yp, np, m.liquidity))
            elif total <= 1.005:
                near.append((total, m.question[:60], yp, np, m.liquidity))
    near.sort()
    under1.sort()
    return priced, near, under1

priced, near, under1 = asyncio.run(scan())
print(f"priced markets (both best asks present, liq>0 denominator): {priced}")
print(f"BEST-ASK sum<1.00 w/ liq>0: {len(under1)}")
for t, q, yp, np, liq in under1[:5]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
print(f"BEST-ASK near-misses (1.00<sum<=1.005, liq>0): {len(near)}")
for t, q, yp, np, liq in near[:8]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
