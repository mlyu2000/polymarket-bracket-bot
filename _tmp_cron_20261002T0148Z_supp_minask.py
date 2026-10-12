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
    dt = time.time() - t0

    rows = []
    skipped = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            skipped += 1
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    print(f"⏱ fetch {len(markets)} markets + books in {dt:.1f}s (skipped {skipped} with empty side)")
    print(f"🌎 GLOBAL MIN best-ask sum (true floor): {rows[0][0]:.4f}" if rows else "no rows")
    priced = [r for r in rows]
    lt1 = [r for r in priced if r[0] < 1.0]
    print(f"📈 markets priced: {len(priced)} | sum<1.00: {len(lt1)} | sum≤1.005: {sum(1 for r in priced if r[0] <= 1.005)}")
    print("--- 10 lowest best-ask sums ---")
    for total, q, yp, np_, liq in rows[:10]:
        flag = " 🔴BRACKET" if total < 1.0 else (" 🟡" if total <= 1.005 else "")
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}{flag}")
    print("--- any true brackets ---")
    for total, q, yp, np_, liq in lt1:
        print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")

asyncio.run(scan())
