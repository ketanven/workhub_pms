from django.test import Client
import json

c = Client()
res = c.post('/api/admin/login/', json.dumps({"email": "admin@workhub.com", "password": "password"}), content_type="application/json")
print("Login Status:", res.status_code)
try:
    data = res.json()
except:
    print("Login Response Failed to parse JSON:", res.content)
    exit(1)

token = data['data']['access']

res2 = c.get('/api/admin/profile/', HTTP_AUTHORIZATION=f'Bearer {token}')
print("Profile Status:", res2.status_code)
try:
    print("Profile Response:", json.dumps(res2.json(), indent=2))
except:
    print("Profile Response Failed to parse JSON:", res2.content)
