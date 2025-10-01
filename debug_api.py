# file: debug_api.py
import os
import requests

def test_apis():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    print(f"API Key: {api_key[:8]}...")
    
    # Test 1: Geocoding API (we know this works)
    print("\n1. Testing Geocoding API...")
    try:
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {'q': 'London,GB', 'limit': 1, 'appid': api_key}
        geo_response = requests.get(geo_url, params=geo_params, timeout=10)
        print(f"   Status: {geo_response.status_code}")
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            print(f"   ✅ Success! Coordinates: {lat}, {lon}")
        else:
            print(f"   ❌ Failed: {geo_response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Current Weather API
    print("\n2. Testing Current Weather API...")
    try:
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather_params = {'lat': 51.5074, 'lon': -0.1278, 'units': 'metric', 'appid': api_key}
        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        print(f"   Status: {weather_response.status_code}")
        print(f"   Response: {weather_response.text[:200]}")
        if weather_response.status_code == 200:
            print("   ✅ Success! Weather API works")
        else:
            print("   ❌ Weather API failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    test_apis()