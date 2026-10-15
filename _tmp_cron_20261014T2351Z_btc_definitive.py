"""Resolve the BTC mystery definitively:
- fetch events bitcoin-above-on-october-15-2026 / -16-2026 by slug
- dump market-level active/closed/volume/liquidity for the $72,000 strikes
- fetch live CLOB books for those markets (min asks both legs)"""
import asyncio

import httpx

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        for slug in ("bitcoin-above-on-october-15-2026",
                     "bitcoin-above-on-october-16-2026"):
            r = await client.get(f"{GAMMA}/events", params={"slug": slug})
            r.raise_for_status()
            evs = r.json()
            if not evs:
                print(f"EVENT {slug}: NOT FOUND")
                continue
            ev = evs[0]
            print(f"EVENT {slug}: closed={ev.get('closed')} active={ev.get('active')} "
                  f"endDate={ev.get('endDate')}")
            for m in ev.get("markets", []):
                q = str(m.get("question", ""))
                if "72,000" not in q:
                    continue
                print(f"  MKT {q!r}")
                print(f"    closed={m.get('closed')} active={m.get('active')} "
                      f"accepting_orders={m.get('acceptingOrders')} "
                      f"volume={m.get('volume')} liq={m.get('liquidity')} "
                      f"endDate={m.get('endDate')}")
                ids = m.get("clobTokenIds")
                if isinstance(ids, str):
                    import json as _j
                    ids = _j.loads(ids)
                if not ids:
                    continue
                for tid in ids[:2]:
                    rb = await client.get(f"{CLOB}/book", params={"token_id": tid})
                    try:
                        b = rb.json()
                        asks = b.get("asks") or []
                        bids = b.get("bids") or []
                        mn = min((float(a["price"]) for a in asks), default=None)
                        print(f"    token {tid[:12]}... asks={len(asks)} bids={len(bids)} "
                              f"min_ask={mn}")
                    except Exception as e:
                        print(f"    token {tid[:12]}... book error: {e}")
            await asyncio.sleep(0.2)


asyncio.run(main())
