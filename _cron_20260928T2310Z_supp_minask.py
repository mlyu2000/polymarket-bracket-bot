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
    scan_time = time.time() - t0

    near = []
    lt1 = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            npr = min(float(a['price']) for a in no_book.asks)
            total = yp + npr
            if total < 1.0:
                lt1.append((total, m.question[:60], yp, npr, m.liquidity))
            elif total <= 1.005:
                near.append((total, m.question[:60], yp, npr, m.liquidity))
    near.sort()
    lt1.sort()
    print(f"[min-ask corrected] {priced}/{len(markets)} markets priced in {scan_time:.1f}s")
    print(f"TRUE BRACKETS sum<1.000 (min best ask): {len(lt1)}")
    for t, q, yp, npr, liq in lt1[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
    print(f"Near-misses 1.000-1.005 (min best ask): {len(near)}")
    for t, q, yp, npr, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")

asyncio.run(scan())
