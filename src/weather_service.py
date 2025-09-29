import os
import requests
from typing import Dict, List, Any
from .exceptions import ConfigurationError, GeoCodingError, WeatherAPIError, NetworkError

class WeatherService:
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ConfigurationError("OPENWEATHER_API_KEY environment variable is not set")
        
        self.geocoding_base_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.one_call_base_url = "https://api.openweathermap.org/data/3.0/onecall"
    
    def get_coordinates(self, city: str, country: str) -> tuple[float, float]:

        try:
            params = {
                'q': f"{city},{country}",
                'limit': 1,
                'appid': self.api_key
            }
            
            response = requests.get(self.geocoding_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                raise GeoCodingError(f"City '{city}' in country '{country}' not found")
            
            location = data[0]
            return location['lat'], location['lon']
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                raise NetworkError("Network error: Unable to connect to weather service") from e
            elif isinstance(e, requests.exceptions.Timeout):
                raise NetworkError("Request timeout: Weather service is not responding") from e
            else:
                raise NetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            if isinstance(e, GeoCodingError):
                raise
            raise GeoCodingError(f"Geocoding failed: {str(e)}") from e
    
    def get_weather_forecast(self, lat: float, lon: float) -> Dict[str, Any]:

        try:
            params = {
                'lat': lat,
                'lon': lon,
                'exclude': 'minutely,hourly,alerts',
                'units': 'metric',
                'appid': self.api_key
            }
            
            response = requests.get(self.one_call_base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                raise WeatherAPIError("Invalid API key. Please check your OPENWEATHER_API_KEY")
            elif response.status_code == 429:
                raise WeatherAPIError("API rate limit exceeded. Please try again later")
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                raise NetworkError("Network error: Unable to connect to weather service") from e
            elif isinstance(e, requests.exceptions.Timeout):
                raise NetworkError("Request timeout: Weather service is not responding") from e
            else:
                raise NetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            if isinstance(e, WeatherAPIError):
                raise
            raise WeatherAPIError(f"Weather API call failed: {str(e)}") from e
    
    def get_weather_data(self, city: str, country: str) -> Dict[str, Any]:

        lat, lon = self.get_coordinates(city, country)
        weather_data = self.get_weather_forecast(lat, lon)
        
        return {
            'city': city,
            'country': country,
            'coordinates': {'lat': lat, 'lon': lon},
            'current': weather_data.get('current', {}),
            'daily': weather_data.get('daily', [])[:3]  # Next 3 days
        }