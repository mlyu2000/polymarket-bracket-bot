"""Where did 'Bitcoin above $72,000 on October 16' go?
Active-set = top-N binary markets by volume desc (active=true, closed=false).
Paginate past the scan's 500-market window and search for BTC strikes."""
import asyncio
import json

import httpx

GAMMA = "https://gamma-api.polymarket.com"


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        found = []
        total = 0
        for offset in range(0, 1000, 100):
            resp = await client.get(
                f"{GAMMA}/markets",
                params={
                    "limit": 100, "offset": offset,
                    "active": "true", "closed": "false",
                    "order": "volume", "ascending": "false",
                },
            )
            resp.raise_for_status()
            raw = resp.json()
            if not raw:
                break
            total += len(raw)
            for rank, m in enumerate(raw):
                q = str(m.get("question", ""))
                if "bitcoin" in q.lower() or "72,000" in q or "72k" in q.lower():
                    found.append((offset + rank, q[:70], m.get("volume"),
                                  m.get("liquidity"), m.get("closed")))
            await asyncio.sleep(0.2)
    print(f"scanned {total} active binary-ranked markets (volume desc)")
    if not found:
        print("NO bitcoin/72,000 market anywhere in top-1000 by volume "
              "-> the above-$72k Oct-16 market is NOT active/closed=false "
              "in the volume ranking (i.e. it CLOSED or was pulled)")
    for f in found:
        print(f"  rank~{f[0]}: {f[1]!r} vol={f[2]} liq={f[3]} closed={f[4]}")


asyncio.run(main())
