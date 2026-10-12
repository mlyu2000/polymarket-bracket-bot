import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def diag():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    empty_yes = empty_no = both_empty = 0
    sample = []
    for m, (yb, nb) in zip(markets, all_books):
        y_empty = not (yb and yb.asks)
        n_empty = not (nb and nb.asks)
        if y_empty: empty_yes += 1
        if n_empty: empty_no += 1
        if y_empty and n_empty: both_empty += 1
        if len(sample) < 5 and not y_empty and not n_empty:
            sample.append((m.question[:40], float(yb.asks[0]['price']), float(nb.asks[0]['price'])))
    print(f"markets={len(markets)}")
    print(f"empty_yes_asks={empty_yes} empty_no_asks={empty_no} both_empty={both_empty}")
    print("sample valid books (yes+no asks):")
    for q, yp, np in sample:
        print(f"  {yp:.3f}+{np:.3f}={yp+np:.3f} | {q}")

asyncio.run(diag())
