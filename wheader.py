from datetime import datetime
import json
import os
from dotenv import load_dotenv
import requests
import random

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

CACHE_FILE = "weather_cache.json"
CACHE_DURATION_SECONDS = 5 * 3600


def load_cache():
  if os.path.exists(CACHE_FILE):
    try:
      with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except json.JSONDecodeError:
      return {}
  return {}


def save_cache(cache_data):
  with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(cache_data, f, indent=4, ensure_ascii=False)


def get_weather(city_name):
  cache = load_cache()
  city_key = city_name.strip().lower()
  current_time = datetime.now().timestamp()

  if city_key in cache:
    cached_entry = cache[city_key]
    time_difference = current_time - cached_entry["timestamp"]

    if time_difference < CACHE_DURATION_SECONDS:
      print("\n[Cache Hit]:")
      return cached_entry

  print("\n[API Request] Weather API...")
  url = "https://api.weatherapi.com/v1/current.json"
  params = {"key": WEATHER_API_KEY, "q": city_name}

  response = requests.get(url, params=params)

  if response.status_code == 200:
    data = response.json()
    weather_data = {"state": data["location"]["region"],"condition": data["current"]["condition"]["text"],"temp_c": data["current"]["temp_c"],"humidity": data["current"]["humidity"],"timestamp": current_time,}
    cache[city_key] = weather_data
    save_cache(cache)
    return weather_data
  else:
    print(f"Failed to fetch weather data. Status Code: {response.status_code}")
    return None

def download_weather_image(query_text, output_filename="weather_image.jpg"):
  print(f"\n[Pixabay API]: '{query_text}'...")

  url = "https://pixabay.com/api/"
  params = {"key": PIXABAY_API_KEY,"q": query_text,"safesearch": "true","image_type": "photo","per_page": 3,}

  response = requests.get(url, params=params)

  if response.status_code != 200:
    print(f"Pixabay request failed. Status Code: {response.status_code}")
    return

  data = response.json()
  hits = data.get("hits", [])

  if not hits:
    print(f" '{query_text}'")
    return
  selected_hit = random.choice(hits)
  image_url = selected_hit["webformatURL"]
  print(f": {image_url}")

  img_response = requests.get(image_url)

  if img_response.status_code == 200:
    with open(output_filename, "wb") as f:
      f.write(img_response.content)
    print(f"saved {output_filename}")
  else:
    print(f" Status Code: {img_response.status_code}")
city = input("Enter city name: ")
weather = get_weather(city)

if weather:
  print(f"State/Region: {weather['state']}")
  print(f"Condition: {weather['condition']}")
  print(f"Temperature: {weather['temp_c']}°C")
  print(f"Humidity: {weather['humidity']}%")
  download_weather_image(weather["condition"])