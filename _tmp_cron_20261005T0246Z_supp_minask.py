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
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

n, priced, rows = asyncio.run(scan())
print(f"markets={n} priced={priced}")
br = [r for r in rows if r[0] < 1.0]
print(f"true_brackets(min-ask sum<1.00)={len(br)}")
for t,q,yp,np_,liq in br[:10]:
    print(f"  BRACKET {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("floor(top8):")
for t,q,yp,np_,liq in rows[:8]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
