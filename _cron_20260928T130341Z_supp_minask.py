import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from models import OrderBook

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            sums.append((ya+na, m.question[:50], ya, na, m.liquidity))
    sums.sort()
    return len(markets), sums

n, sums = asyncio.run(scan())
near = [s for s in sums if s[0] <= 1.005]
under1 = [s for s in sums if s[0] < 1.0]
print(f"[supp min-ask] markets priced: {len(sums)}/{n}")
print(f"[supp min-ask] true brackets (sum<1.0): {len(under1)}")
for total, q, yp, np, liq in under1[:5]:
    print(f"  SUM<1 {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"[supp min-ask] near-misses (<=1.005): {len(near)}")
for total, q, yp, np, liq in near[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"[supp min-ask] best floor overall: {sums[0][0]:.4f} | {sums[0][1]}")
