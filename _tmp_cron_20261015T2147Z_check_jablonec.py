"""Targeted verification: resolve the drop of Spread: FK Jablonec (-5.5) from
top-12 (was 1.008 liq 12978.8 at 21:27Z). Re-fetch and check TWO-SIDED state.
Also re-verify floor holder (Lagarde) and previous near-floor markets."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

CANDIDATES = [
    "Spread: FK Jablonec (-5.5)",
    "Spread: FK Jablonec (-4.5)",
    "Will Christine Lagarde win the 2027 French presidential election?",
    "Will the highest temperature in Sao Paulo be 31",
    "Bitcoin more valuable than any company",
    "Exact Score: FC Bayern M",
]


async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    by_q = {m.question: m for m in markets}
    picks = []
    for c in CANDIDATES:
        m = by_q.get(c)
        if not m:
            for q, mm in by_q.items():
                if q.startswith(c[:40]):
                    m = mm
                    break
        if m:
            picks.append(m)
        else:
            print(f"MISSING FROM ACTIVE-500: {c}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in picks]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m, (yb, nb) in zip(picks, all_books):
        ya = [float(a['price']) for a in yb.asks] if yb and yb.asks else []
        na = [float(a['price']) for a in nb.asks] if nb and nb.asks else []
        state = "TWO-SIDED" if (ya and na) else ("YES-only" if ya else ("NO-only" if na else "EMPTY"))
        yp = min(ya) if ya else None
        np_ = min(na) if na else None
        s = f"{yp+np_:.3f}" if (yp is not None and np_ is not None) else "n/a"
        print(f"{state:11} | minY={yp} minN={np_} sum={s} | liq={m.liquidity} | {m.question[:55]}")


asyncio.run(scan())
