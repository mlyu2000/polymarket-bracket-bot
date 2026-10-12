import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find_min():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    bests = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            bests.append((total, m.liquidity, m.question[:60], yes_price, no_price))
    bests.sort()
    print(f"Checked {len(bests)} markets with books")
    for total, liq, q, yp, np in bests[:20]:
        print(f"{total:.4f} liq={liq:.0f} Yes@{yp:.3f} No@{np:.3f} | {q}")

asyncio.run(find_min())
