"""Direct public Gamma search: status of 'Bitcoin above $72,000 on October 16' —
in the floor tier at 23:37Z (sole leader, 1.001), absent from the 23:52Z top-500
volume-sorted active sample."""
import asyncio
import httpx


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://gamma-api.polymarket.com/public-search",
            params={"q": "bitcoin above 72000", "limit_per_type": 5},
        )
        resp.raise_for_status()
        d = resp.json()
    events = d.get("events", [])
    print(f"events={len(events)}")
    for ev in events[:5]:
        print("EVENT:", ev.get("title"), "| closed:", ev.get("closed"),
              "| active:", ev.get("active"), "| volume:", ev.get("volume"))
        for m in ev.get("markets", [])[:4]:
            print("   MKT:", str(m.get("question"))[:70],
                  "| closed:", m.get("closed"),
                  "| volume:", m.get("volume"),
                  "| liq:", m.get("liquidity"))


asyncio.run(main())
