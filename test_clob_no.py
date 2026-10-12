import httpx
url = "https://clob.polymarket.com/book?token_id=85143992601946000448809166192852279322616766350775811418663159978958021051194"
resp = httpx.get(url, timeout=10)
print(resp.status_code)
data = resp.json()
print('asks', data.get('asks')[:3])
print('bids', data.get('bids')[:3])
