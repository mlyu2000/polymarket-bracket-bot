"""Targeted verification: confirm mechanism of the two_sided 62->53 drop.
Re-fetch the specific markets that vanished from the 21:08Z top-12 and check
whether their NO-leg still has asks (two-sided) or went bid-only (YES-only).
Resolves 'decrowd' = NO-leg exits (structural) vs 'reorder' = still bookable.
"""
import asyncio, json, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

CANDIDATES = [
    "Will Christine Lagarde win the 2027 French presidential election?",  # floor holder (should stay)
    "Spread: FC Thun (-4.5)",
    "Spread: FC Thun (-5.5)",
    "Spread: FK Jablonec (-4.5)",
    "Spread: FK Jablonec (-5.5)",
    "Spread: FC K\u00f8benhavn (-4.5)",
    "Exact Score: Manchester City FC 0 - 2 Ipswich Town FC?",
    "Will Democrats win 12 or more House seats in Pennsylvania in the 2026 midterm election?",
]


async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    by_q = {m.question: m for m in markets}
    picks = []
    for c in CANDIDATES:
        # exact match first, else prefix match
        m = by_q.get(c)
        if not m:
            for q, mm in by_q.items():
                if q.startswith(c[:55]):
                    m = mm
                    break
        if m:
            picks.append(m)
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
