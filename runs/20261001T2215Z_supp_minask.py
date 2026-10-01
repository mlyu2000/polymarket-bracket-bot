# Supplement: near-misses recomputed with BEST asks (min price).
# CLOB /book returns asks DESC-sorted, so asks[0] is the WORST ask (~0.999)
# and the verbatim near-miss block systematically overstates totals.
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets = []
    near = []
    priced = 0
    min_sum = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if min_sum is None or total < min_sum[0]:
                min_sum = (total, m.question[:60], yp, np_, m.liquidity)
            if total < 1.00 and m.liquidity >= Config.MIN_LIQUIDITY_USDC and 0 < yp < 1 and 0 < np_ < 1:
                brackets.append((total, m.question[:60], yp, np_, m.liquidity))
            elif total <= 1.005 and m.liquidity >= Config.MIN_LIQUIDITY_USDC:
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    brackets.sort()
    near.sort()
    return len(markets), priced, brackets, near, min_sum

n, priced, brackets, near, min_sum = asyncio.run(scan())
print(f"markets: {n} | priced books: {priced}")
print(f"true brackets (best asks sum<1.00, liq ok): {len(brackets)}")
for total, q, yp, np_, liq in brackets[:10]:
    print(f"  🟢 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"near-misses on best asks (<=1.005): {len(near)}")
for total, q, yp, np_, liq in near[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if min_sum:
    print(f"global floor: {min_sum[0]:.4f} | Yes@{min_sum[2]:.3f} No@{min_sum[3]:.3f} | liq={min_sum[4]} | {min_sum[1]}")
