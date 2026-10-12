import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from models import OrderBook

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    print(f"markets with both books: {len(rows)}")
    print("TOP 12 best true sum (min-ask yes + min-ask no):")
    for t, q, yp, np_, liq in rows[:12]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    lt1 = [r for r in rows if r[0] < 1.0]
    le1005 = [r for r in rows if r[0] <= 1.005]
    print(f"count sum<1.00: {len(lt1)} | count sum<=1.005: {len(le1005)}")

asyncio.run(supp())
