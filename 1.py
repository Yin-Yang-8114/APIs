import requests
from datetime import datetime
payload = {"name": "Chaim", "age": 22}
response = requests.post("https://google.com", json=payload)

# response = requests.put("https://api.example.com/items/1", json=update_data)
# response = requests.patch("https://api.example.com/items/1", json=patch_data)
# response = requests.delete("https://api.example.com/items/1")
# response = requests.post("https://api.example.com/tasks", json=payload)
# response = requests.get("https://api.example.com/data", headers=custom_headers)
print(response.status_code)
current_time = datetime.now().timestamp()
print(current_time)