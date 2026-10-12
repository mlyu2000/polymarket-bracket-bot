import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
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
        # asks are DESC-sorted; best ask = min price
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))

    rows.sort()
    return len(markets), priced, rows

async def main():
    markets, priced, rows = await scan()
    print(f"Markets fetched: {markets} | priced (both sides have asks): {priced}")
    if rows:
        print(f"True best-ask floor: sum={rows[0][0]:.4f}")
        print("Top 10 cheapest YES+NO brackets (best asks):")
        for total, q, yp, np, liq in rows[:10]:
            flag = " <<< BRACKET <1.00" if total < 1.0 else (" <=1.005" if total <= 1.005 else "")
            print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}{flag}")
        n_below = sum(1 for r in rows if r[0] < 1.0)
        n_nm = sum(1 for r in rows if 1.0 <= r[0] <= 1.005)
        print(f"Count sum<1.00: {n_below} | Count 1.00<=sum<=1.005: {n_nm}")

asyncio.run(main())
