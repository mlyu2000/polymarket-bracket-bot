"""Public-search deeper: find the October 'Bitcoin above ___' event and its
closed/endDate status to explain the 23:37Z->23:52Z disappearance."""
import asyncio

import httpx


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://gamma-api.polymarket.com/public-search",
            params={"q": "bitcoin above", "limit_per_type": 30},
        )
        resp.raise_for_status()
        d = resp.json()
    events = d.get("events", [])
    oct_events = [e for e in events if "october" in str(e.get("title", "")).lower()]
    print(f"total events={len(events)} october events={len(oct_events)}")
    for e in oct_events:
        print("EVENT:", e.get("title"), "| slug:", e.get("slug"),
              "| closed:", e.get("closed"), "| endDate:", e.get("endDate"),
              "| volume:", e.get("volume"))
        for m in e.get("markets", [])[:3]:
            print("   MKT:", str(m.get("question"))[:60],
                  "| closed:", m.get("closed"), "| volume:", m.get("volume"))


asyncio.run(main())
