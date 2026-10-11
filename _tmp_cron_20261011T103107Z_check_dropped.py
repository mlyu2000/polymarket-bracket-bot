import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    keys = ['Paris', 'Konyaspor', 'Troyes']
    found = {k: [] for k in keys}
    for m in markets:
        for k in keys:
            if k in m.question:
                found[k].append(m)
    for k, ms in found.items():
        for m in ms:
            yb = await api.fetch_order_book(m.clob_token_ids[0])
            nb = await api.fetch_order_book(m.clob_token_ids[1])
            yasks = [float(a['price']) for a in (yb.asks if yb and yb.asks else [])]
            nasks = [float(a['price']) for a in (nb.asks if nb and nb.asks else [])]
            ymin = min(yasks) if yasks else None
            nmin = min(nasks) if nasks else None
            total = (ymin + nmin) if (ymin is not None and nmin is not None) else None
            print(f"{m.question[:70]}")
            print(f"  yes_min={ymin} no_min={nmin} sum={total if total is None else round(total,4)} liq={m.liquidity}")
            print(f"  yes_asks_top5={sorted(yasks)[:5] if yasks else 'EMPTY'} no_asks_top5={sorted(nasks)[:5] if nasks else 'EMPTY'}")

asyncio.run(check())
