import requests

url = "http://127.0.0.1:5000/register"
data = {
    "username": "adminUser",
    "password": "12345678",
    "role": "admin"
}

response = requests.post(url, json=data)
print(response.json())
