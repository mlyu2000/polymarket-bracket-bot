import httpx
url = "https://clob.polymarket.com/book?token_id=92150208931243546375084460585031574741462595456197645733341477538401127595171"
resp = httpx.get(url, timeout=10)
print(resp.status_code)
data = resp.json()
print('asks', data.get('asks')[:3])
print('bids', data.get('bids')[:3])
