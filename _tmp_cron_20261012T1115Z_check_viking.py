import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        if 'Viking' in m.question:
            print(f"MARKET: {m.question}")
            print(f"  active={getattr(m, 'active', '?')} closed={getattr(m, 'closed', '?')} liquidity={m.liquidity:.0f}")
            books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yb, nb = books[0]
            print(f"  YES book asks: {len(yb.asks) if yb and yb.asks else 0}")
            if yb and yb.asks:
                ya = sorted(float(a['price']) for a in yb.asks)
                print(f"    min ask={ya[0]:.4f} max ask={ya[-1]:.4f} | first5={ya[:5]}")
            print(f"  NO book asks: {len(nb.asks) if nb and nb.asks else 0}")
            if nb and nb.asks:
                na = sorted(float(a['price']) for a in nb.asks)
                print(f"    min ask={na[0]:.4f} max ask={na[-1]:.4f} | first5={na[:5]}")

asyncio.run(check())
