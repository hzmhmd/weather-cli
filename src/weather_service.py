import os
import requests
from typing import Dict, Any
from src.exceptions import ConfigurationError, GeoCodingError, WeatherAPIError, NetworkError

class WeatherService:
    """Service class to handle OpenWeatherMap API interactions"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ConfigurationError("OPENWEATHER_API_KEY environment variable is not set")
        
        self.geocoding_base_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.weather_base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_coordinates(self, city: str, country: str) -> tuple[float, float]:
        """
        Convert city and country to latitude and longitude using Geocoding API
        """
        try:
            params = {
                'q': f"{city},{country}",
                'limit': 1,
                'appid': self.api_key
            }
            
            response = requests.get(self.geocoding_base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                raise WeatherAPIError("Invalid API key")
                
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                raise GeoCodingError(f"City '{city}' in country '{country}' not found")
            
            location = data[0]
            return location['lat'], location['lon']
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}") from e
        except GeoCodingError:
            raise  
        except Exception as e:
            raise GeoCodingError(f"Geocoding failed: {str(e)}") from e
    
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather using Current Weather API
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'units': 'metric',
                'appid': self.api_key
            }
            
            response = requests.get(self.weather_base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                raise WeatherAPIError("Invalid API key. Please check your OPENWEATHER_API_KEY")
            elif response.status_code == 429:
                raise WeatherAPIError("API rate limit exceeded. Please try again later")
                
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}") from e
        except WeatherAPIError:
            raise  
        except Exception as e:
            raise WeatherAPIError(f"Weather API call failed: {str(e)}") from e
    
    def get_weather_data(self, city: str, country: str) -> Dict[str, Any]:
        """
        Get complete weather data for a city
        """
        lat, lon = self.get_coordinates(city, country)
        current_weather = self.get_current_weather(lat, lon)
        
        return {
            'city': city,
            'country': country,
            'coordinates': {'lat': lat, 'lon': lon},
            'current': current_weather
        }