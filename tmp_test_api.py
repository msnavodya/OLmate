import requests
import time

email = f"testendpoint+{int(time.time())}@example.com"

for action in ("register","login"):
    if action=="register":
        url='http://localhost:8001/api/auth/register'
        data={"name":"Test Endpoint","email":email,"password":"password123"}
    else:
        url='http://localhost:8001/api/auth/login'
        data={"email":email,"password":"password123"}
    resp=requests.post(url,json=data)
    print(action, resp.status_code, resp.text)
