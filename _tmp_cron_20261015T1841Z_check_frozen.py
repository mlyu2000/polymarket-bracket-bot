"""Targeted: verify Bitcoin>any-co book is still byte-identical (frozen) + NFL futures cluster identical-liq check."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    targets = [m for m in markets if 'more valuable than any company' in m.question]
    for m in targets:
        print(f"Q: {m.question}")
        print(f"RAW liq: {m.liquidity!r}")
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in targets]
    books = await api.fetch_order_books_batch(pairs)
    for m, (yb, nb) in zip(targets, books):
        if yb and yb.asks:
            ymin = min(float(a['price']) for a in yb.asks)
            ymin_sz = [a['size'] for a in yb.asks if float(a['price']) == ymin]
            print(f"Yes min-ask {ymin} size {ymin_sz[:3]} | n_asks {len(yb.asks)}")
        if nb and nb.asks:
            nmin = min(float(a['price']) for a in nb.asks)
            nmin_sz = [a['size'] for a in nb.asks if float(a['price']) == nmin]
            print(f"No  min-ask {nmin} size {nmin_sz[:3]} | n_asks {len(nb.asks)}")
    # NFL futures cluster at 1.041: check raw liq equality across the 10 teams
    nfl = [m for m in markets if 'finish the 2026-27 NFL regular season' in m.question]
    print(f"NFL futures cluster: {len(nfl)} markets")
    for m in nfl:
        print(f"  {m.question[:70]} liq={m.liquidity!r}")

asyncio.run(main())
