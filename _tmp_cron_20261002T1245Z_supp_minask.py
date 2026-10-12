# Supplementary: near-misses recomputed with MIN ask (asks[0] is DESC-worst per API ordering)
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    lt1 = []
    no_asks = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            no_asks += 1
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        if tot < 1.0:
            lt1.append((tot, m.question[:55], yp, np_, m.liquidity))
        elif tot <= 1.005:
            near.append((tot, m.question[:55], yp, np_, m.liquidity))
    near.sort()
    lt1.sort()
    print(f"markets={len(markets)} no_asks_sides={no_asks}")
    print(f"true sum<1.00 (min-ask, before detector guards): {len(lt1)}")
    for t, q, y, n, l in lt1[:10]:
        print(f"  {t:.4f} | Y@{y:.3f} N@{n:.3f} | liq={l} | {q}")
    print(f"near-misses 1.000<sum<=1.005: {len(near)}")
    for t, q, y, n, l in near[:10]:
        print(f"  {t:.4f} | Y@{y:.3f} N@{n:.3f} | liq={l} | {q}")

asyncio.run(scan())
