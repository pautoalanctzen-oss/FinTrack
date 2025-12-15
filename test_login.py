import requests, random
BASE = "http://127.0.0.1:8000"
username = f"auto_user_{random.randint(1000,9999)}"
email = f"{username}@example.com"
password = "Test123456"

print("Registering:", username)
r = requests.post(f"{BASE}/api/register", data={
    "email": email,
    "username": username,
    "birthdate": "2001-02-03",
    "password": password,
    "confirm_password": password,
})
print("REGISTER:", r.status_code, r.text)

print("Logging in:")
l = requests.post(f"{BASE}/api/login", data={
    "username": username,
    "password": password,
})
print("LOGIN:", l.status_code, l.text)
try:
    print("LOGIN JSON:", l.json())
except Exception as e:
    print("Failed to parse login JSON:", e)
