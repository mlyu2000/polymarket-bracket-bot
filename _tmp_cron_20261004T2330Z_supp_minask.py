# Supplementary: correct near-miss floor using min(asks) since CLOB /book asks are
# DESC-sorted (asks[0] = worst ask ~0.999). Mirrors detector.py logic (min by price).
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    bracketable = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        rows.append((total, m.question[:60], ya, na, m.liquidity))
        # raw sum < 1.00 check (ignores buffers the detector applies)
        if total < 1.00:
            bracketable.append((total, m.question[:60], ya, na, m.liquidity))

    rows.sort()
    print(f"markets_with_both_asks: {len(rows)} / {len(markets)}")
    print(f"raw_sum_below_1.00: {len(bracketable)}")
    for t, q, ya, na, liq in bracketable[:10]:
        print(f"  RAW sum={t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("best floors (min-ask method):")
    for t, q, ya, na, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
