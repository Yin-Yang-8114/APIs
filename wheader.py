from datetime import datetime
import json
import os
import random
from dotenv import load_dotenv
import requests
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

CACHE_FILE = "weather_cache.json"
CACHE_DURATION_SECONDS =3600
WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"
PIXABAY_API_URL = "https://pixabay.com/api/"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}

def save_cache(cache_data):
    with open(CACHE_FILE, "w") as file:
        json.dump(cache_data, file)

def is_cache_valid(cached_entry):
    if not cached_entry or "timestamp" not in cached_entry:
        return False
    current_time = datetime.now().timestamp()
    return (current_time - cached_entry["timestamp"]) < CACHE_DURATION_SECONDS


def fetch_weather_from_api(city_name):
    params = {"key": WEATHER_API_KEY, "q": city_name}
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print(f"Weather API request error: {error}")
        return None


def parse_weather_data(api_response):
    return {"state": api_response["location"]["region"],"condition": api_response["current"]["condition"]["text"],"temp_c": api_response["current"]["temp_c"],"humidity": api_response["current"]["humidity"],"timestamp": datetime.now().timestamp(),}

def get_weather(city_name):
    city_key = city_name.strip().lower()
    cache = load_cache()

    if city_key in cache and is_cache_valid(cache[city_key]):
        print("chash")
        return cache[city_key]

    print("api request ")
    raw_data = fetch_weather_from_api(city_name)
    if not raw_data:
        return None

    weather_data = parse_weather_data(raw_data)
    cache[city_key] = weather_data
    save_cache(cache)
    return weather_data

def fetch_image_url(query_text):
    params = {"key": PIXABAY_API_KEY,"q": query_text,"safesearch": "true","image_type": "photo","per_page": 3,}
    try:
        response = requests.get(PIXABAY_API_URL, params=params)
        response.raise_for_status()
        hits = response.json().get("hits", [])
        if not hits:
            print(f"no image for '{query_text}'")
            return None
        return random.choice(hits)["webformatURL"]
    except requests.RequestException as error:
        print(f"request error: {error}")
        return None


def save_image_to_file(image_url, output_filename="weather_image.jpg"):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        with open(output_filename, "wb") as file:
            file.write(response.content)
        print(f"imag saved as '{output_filename}'")
    except requests.RequestException as error:
        print(f"Failed download: {error}")

def download_weather_image(query_text, output_filename="weather_image.jpg"):
    image_url = fetch_image_url(query_text)
    if image_url:
        save_image_to_file(image_url, output_filename)

def display_weather(weather_data):
    print(f"State/Region: {weather_data['state']}")
    print(f"Condition: {weather_data['condition']}")
    print(f"Temperature: {weather_data['temp_c']}°C")
    print(f"Humidity: {weather_data['humidity']}%")

def main():
    city = input("enter city name: ").strip()
    if not city:
        print("city name cannot be empty")
        return
    weather = get_weather(city)
    if weather:
        display_weather(weather)
        download_weather_image(weather["condition"])

main()