import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    floors = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yb.asks)
            npx = min(float(a['price']) for a in nb.asks)
            s = yp + npx
            floors.append((s, m.question[:60], yp, npx, m.liquidity))
            priced += 1
    floors.sort()
    return {'markets': len(markets), 'priced': priced, 'floors': floors}

result = asyncio.run(scan())
floors = result['floors']
print(f"Markets: {result['markets']}, priced pairs: {result['priced']}")
if floors:
    ts = [f[0] for f in floors]
    under1 = sum(1 for t in ts if t < 1.0)
    le1001 = sum(1 for t in ts if t <= 1.001)
    le1005 = sum(1 for t in ts if t <= 1.005)
    le101 = sum(1 for t in ts if t <= 1.01)
    print(f"Sum<1.00: {under1} | Sum<=1.001: {le1001} | <=1.005: {le1005} | <=1.01: {le101}")
    print(f"Floor: {ts[0]:.4f} | Median: {ts[len(ts)//2]:.4f}")
    print("Top 10 best (min-ask Yes+No):")
    for s, q, yp, npx, liq in floors[:10]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{npx:.3f} | liq={liq:,.0f} | {q}")
