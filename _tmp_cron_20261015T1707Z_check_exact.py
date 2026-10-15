"""Targeted check: what happened to the exact-score / frozen-book markets that
were in the 1.005-1.010 band at 16:51Z but vanished from the top25 at 17:08Z.
Re-fetch their books and report current min-ask sums (or dropped legs)."""
import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

TARGETS = [
    'Exact Score: Bologna FC 1909 4 - 3',
    'Exact Score: Bologna FC 1909 3 - 4',
    'Exact Score: Brentford FC 1 - 5',
    'Exact Score: Brentford FC 4 - 4',
    'Exact Score: Brentford FC 5 - 1',
    'Exact Score: Brentford FC 3 - 4',
    'Exact Score: Brentford FC 4 - 3',
    'Exact Score: Venezia FC 4 - 3',
    'Exact Score: Venezia FC 4 - 1',
    'Exact Score: Venezia FC 2 - 5',
    'Exact Score: Venezia FC 3 - 4',
    'Exact Score: RC Strasbourg Alsa',
]


async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    tgt = [m for m in markets if any(m.question.startswith(t) for t in TARGETS)]
    print(f'matched {len(tgt)} exact-score markets')
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in tgt]
    books = await api.fetch_order_books_batch(token_pairs)

    def best(book):
        if not book or not book.asks:
            return None
        return min(float(a['price']) for a in book.asks)

    prev = json.load(open('runs/_tmp_cron_20261015T165128Z_supp_data.json'))
    prevq = {r[1]: (r[0], r[4]) for r in prev['rows']}
    for m, (yb, nb) in zip(tgt, books):
        y, n = best(yb), best(nb)
        pt, pl = prevq.get(m.question[:55], (None, None))
        if y is None or n is None:
            status = f'YES_ask={"none" if y is None else y} NO_ask={"none" if n is None else n}'
            tot = None
        else:
            tot = y + n
            status = ''
        p = f'{pt:.3f}/{pl:.1f}' if pt else 'not-in-prev'
        if tot is None:
            print(f'  {p} -> DROPPED LEG | {status} | {m.question[:50]}')
        else:
            mark = ' <<< WORSENED PAST 1.030' if tot > 1.030 else ''
            print(f'  {p} -> {tot:.3f} (Y{y:.3f} N{n:.3f}) liq={m.liquidity:.1f}{mark} | {m.question[:50]}')


asyncio.run(main())
