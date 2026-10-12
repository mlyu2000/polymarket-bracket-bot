import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    n_nopair = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            n_nopair += 1
            continue
        # CLOB /book asks are DESC-sorted -> true best ask = min
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))

    rows.sort()
    print(f"markets={len(markets)} priced_pairs={len(rows)} missing_book={n_nopair}")
    print("TRUE floor top-10 (sum = min yes ask + min no ask):")
    for t, q, ya, na, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    under = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"sum<1.00: {len(under)} | sum in [1.00,1.005]: {len(nm)}")
    for t, q, ya, na, liq in nm[:5]:
        print(f"  NEAR {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())
