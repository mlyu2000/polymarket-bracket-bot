import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def sup():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        # best ask = min price (asks are DESC-sorted in the CLOB payload)
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        rows.append((ya + na, m.question[:50], ya, na, m.liquidity))

    rows.sort()
    print(f"priced markets: {priced}")
    if rows:
        print(f"floor (min best-ask sum): {rows[0][0]:.4f}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (best-ask sum <= 1.005): {len(nm)}")
    for s, q, ya, na, liq in nm[:5]:
        print(f"  {s:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"best-ask sums < 1.000: {len(lt1)}")
    for s, q, ya, na, liq in lt1[:5]:
        print(f"  🔴 {s:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(sup())
