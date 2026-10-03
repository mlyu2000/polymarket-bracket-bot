import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    minask = []   # min-ask totals (detector semantics)
    ask0 = []     # asks[0] totals (verbatim-script semantics, DESC => worst asks)
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            ym = min(float(a['price']) for a in yb.asks)
            nm = min(float(a['price']) for a in nb.asks)
            minask.append((ym + nm, m.question[:50]))
            y0 = float(yb.asks[0]['price'])
            n0 = float(nb.asks[0]['price'])
            ask0.append((y0 + n0, m.question[:50]))

    minask.sort(); ask0.sort()
    le1005 = [t for t in minask if t[0] <= 1.005]
    le1010 = [t for t in minask if t[0] <= 1.010]
    lt1000 = [t for t in minask if t[0] < 1.000]
    nm_ask0 = [t for t in ask0 if t[0] <= 1.005]

    print(f"both-sides-priced: {priced}")
    print(f"min-ask floor: {minask[0][0]:.4f} | {minask[0][1]}")
    print(f"min-ask true brackets <1.000: {len(lt1000)}")
    for t, q in lt1000: print(f"  {t:.4f} | {q}")
    print(f"min-ask near-misses <=1.005: {len(le1005)}")
    for t, q in le1005: print(f"  {t:.4f} | {q}")
    print(f"count<=1.010: {len(le1010)}")
    for t, q in le1010: print(f"  {t:.4f} | {q}")
    print(f"best-ask-0 near-misses <=1.005: {len(nm_ask0)}")
    for t, q in nm_ask0: print(f"  {t:.4f} | {q}")

asyncio.run(supp())
