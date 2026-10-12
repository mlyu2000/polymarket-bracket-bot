import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    floors = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if total < 1.0:
                brackets.append((total, m.question[:60], yp, np_, m.liquidity))
            else:
                floors.append((total, m.question[:50], yp, np_, m.liquidity))
    floors.sort()
    brackets.sort()
    print(f"markets={len(markets)} best-ask-floor brackets(<1.00)={len(brackets)}")
    for b in brackets[:10]:
        print(f"  [FLOOR-BRACKET] {b[0]:.4f} | Yes@{b[2]:.3f} No@{b[3]:.3f} | liq={b[4]} | {b[1]}")
    print("true near-misses (best-ask sum <=1.005):")
    nm = [f for f in floors if f[0] <= 1.005]
    print(f"  count={len(nm)}")
    for total, q, yp, np_, liq in nm[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"global best-ask floor min sum: {floors[0][0]:.4f} ({floors[0][1]})" if floors else "no floors")

asyncio.run(scan())
