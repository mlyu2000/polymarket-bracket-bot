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
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        rows.append((tot, m.question[:55], yp, np_, m.liquidity))
        if tot < 1.0:
            brackets.append(rows[-1])
    rows.sort()
    print(f"markets={len(markets)} elapsed={dt:.1f}s (best-ask basis)")
    print(f"BEST-ASK BRACKETS (sum<1.00): {len(brackets)}")
    for tot, q, yp, np_, liq in brackets:
        print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("TOP 10 BEST-ASK TOTALS:")
    for tot, q, yp, np_, liq in rows[:10]:
        print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
