import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    el = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:70], yp, np, m.liquidity))
    rows.sort()
    print(f"min-ask supplementary: {len(markets)} markets, {priced} priced, {el:.1f}s")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"min-ask BRACKETS (sum<1.0): {len(brackets)}")
    for total, q, yp, np, liq in brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("top 8 closest (sum<=1.005):")
    for total, q, yp, np, liq in [r for r in rows if r[0] <= 1.005][:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("overall floor:", rows[0][0] if rows else None)

asyncio.run(scan())
