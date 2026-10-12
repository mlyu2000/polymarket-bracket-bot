"""Cron 20261005T2005Z — supplementary: TRUE best-ask (min) floor + band detail.

Mechanism-agnostic: iterates whatever fields the Market model exposes for
liquidity/question; best ask resolved by min(price) over asks, never by index.
"""
import asyncio, logging
from dataclasses import fields as dc_fields
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)


def fld(obj, *names, default=None):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default


async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        priced += 1
        ysz = min(int(float(a['size'])) for a in yb.asks if float(a['price']) == yp)
        nsz = min(int(float(a['size'])) for a in nb.asks if float(a['price']) == np_)
        rows.append({
            'sum': round(yp + np_, 4),
            'q': str(fld(m, 'question', default='?'))[:70],
            'yes': yp, 'no': np_,
            'ov': min(ysz, nsz),
            'liq': fld(m, 'liquidity', 'liquidity_usdc', 'liquidityNum', default=None),
            'vol': fld(m, 'volume', 'volume_num', 'volumeNum', default=None),
            'active': fld(m, 'active', default=True),
            'closed': fld(m, 'closed', default=False),
        })

    rows.sort(key=lambda r: r['sum'])
    det = BracketDetector()
    print(f"both-sides-priced: {priced} / {len(markets)} markets")
    print("--- TOP 15 (true min-ask sums) ---")
    for r in rows[:15]:
        print(f"{r['sum']:.3f} | yes {r['yes']:.3f} x{r['ov'] if r['yes']<0.5 else '?'} no {r['no']:.3f} | ov={r['ov']} liq={r['liq']} vol={r['vol']} | {r['q']}")
    band = [r for r in rows if r['sum'] <= 1.005]
    print(f"band <=1.005: {len(band)}")
    under = [r for r in rows if r['sum'] < 1.0]
    print(f"sum <1.00 (true brackets by min-ask): {len(under)}")
    for r in under:
        print(f"  *** {r['sum']:.4f} | {r['q']} liq={r['liq']} ov={r['ov']}")
    # cross-check against detector on the 15 lowest-sum markets
    idx = {id(m): (yb, nb) for m, (yb, nb) in zip(markets, books)}
    qmap = {str(fld(m, 'question', default='?'))[:70]: m for m in markets}
    n_det_opps = 0
    for r in rows[:15]:
        m = qmap.get(r['q'])
        if m is None:
            continue
        yb, nb = idx[id(m)]
        opp = det.detect(m, yb, nb)
        if opp:
            n_det_opps += 1
            print(f"  DETECTOR OPP: {opp.total_cost} net={opp.net_edge} shares={opp.max_shares} {r['q']}")
    print(f"detector-opps among top-15: {n_det_opps}")


asyncio.run(main())
