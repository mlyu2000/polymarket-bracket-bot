"""Targeted check: BoJ 50bps leader book, Lagarde floor book, Bitcoin frozen book."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)


async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    targets = []
    for m in markets:
        q = m.question.lower()
        if ('bank of japan decreases interest rates by 50+ bps' in q or
                'lagarde win the 2027 french presidential' in q or
                'bitcoin more valuable than any company' in q):
            targets.append(m)
    for m in targets:
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yb, nb = books[0]
        yb_asks = list(yb.asks) if (yb and yb.asks) else []
        nb_asks = list(nb.asks) if (nb and nb.asks) else []
        ya = [float(a['price']) for a in yb_asks]
        na = [float(a['price']) for a in nb_asks]
        print(f"Q: {m.question[:75]}")
        print(f"  liq={m.liquidity}")
        if ya and na:
            print(f"  min-ask sum={min(ya)+min(na):.4f} (Y min={min(ya)} N min={min(na)})")
            print(f"  yes asks top3: {[(a['price'], a['size']) for a in yb_asks[:3]]}")
            print(f"  no asks top3: {[(a['price'], a['size']) for a in nb_asks[:3]]}")
        else:
            print(f"  yes asks n={len(ya)} no asks n={len(na)} (one-sided/empty)")


asyncio.run(check())
