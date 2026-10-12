import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    watch = ['Sevilla', 'NH-02', 'Hormuz', 'Katowice', 'Bolsonaro', 'Galatasaray']
    print("=== WATCHED MARKETS ===")
    for m, (yb, nb) in zip(markets, all_books):
        if any(w in m.question for w in watch):
            ya = [float(a['price']) for a in (yb.asks or [])] if yb else []
            na = [float(a['price']) for a in (nb.asks or [])] if nb else []
            ny = len(ya) if ya else 0
            nn = len(na) if na else 0
            my = min(ya) if ya else None
            mn = min(na) if na else None
            tot = f"{my+mn:.4f}" if (my is not None and mn is not None) else "n/a"
            print(f"{m.question[:75]}")
            print(f"   yes_asks={ny} no_asks={nn} min_yes={my} min_no={mn} sum={tot} liq={m.liquidity}")
    print("=== NO-ONLY MARKETS ===")
    for m, (yb, nb) in zip(markets, all_books):
        ya = [float(a['price']) for a in (yb.asks or [])] if yb else []
        na = [float(a['price']) for a in (nb.asks or [])] if nb else []
        if na and not ya:
            print(f"{m.question[:80]} | min_no={min(na)} | no_asks={len(na)} | liq={m.liquidity}")

asyncio.run(check())
