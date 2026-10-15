"""Drift probe: what happened to the Musk tweet-count market that held the
floor for 5 consecutive scans (18:03Z-18:04Z @1.0010)?"""
import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)


async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    def best(b):
        if not b or not b.asks:
            return None
        return min(float(a['price']) for a in b.asks)

    hits = []
    for m, (yb, nb) in zip(markets, books):
        q = m.question.lower()
        if 'musk' in q or 'tweet' in q:
            y, n = best(yb), best(nb)
            hits.append({
                'q': m.question[:70],
                'yes': y, 'no': n,
                'total': round(y + n, 4) if (y is not None and n is not None) else None,
                'liq': m.liquidity,
                'two_sided': bool(yb and yb.bids and yb.asks) and bool(nb and nb.bids and nb.asks),
            })
    print(json.dumps(hits, indent=2))


asyncio.run(main())
