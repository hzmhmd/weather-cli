import os
import requests
from typing import Dict, Any
from datetime import datetime
from src.exceptions import ConfigurationError, GeoCodingError, WeatherAPIError, NetworkError

class WeatherService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ConfigurationError("OPENWEATHER_API_KEY environment variable is not set")
        
        self.geocoding_base_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.weather_base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_base_url = "https://api.openweathermap.org/data/2.5/forecast"
    
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

    def get_weather_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get 5-day weather forecast
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'units': 'metric',
                'appid': self.api_key
            }
            
            response = requests.get(self.forecast_base_url, params=params, timeout=10)
            
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
        Get complete weather data for a city with 3-day forecast
        """
        lat, lon = self.get_coordinates(city, country)
        current_weather = self.get_current_weather(lat, lon)
        forecast_data = self.get_weather_forecast(lat, lon)
        
        # Process forecast to get daily data
        daily_forecast = self._process_forecast_to_daily(forecast_data)
        
        return {
            'city': city,
            'country': country,
            'coordinates': {'lat': lat, 'lon': lon},
            'current': current_weather,
            'daily': daily_forecast[:3]  # Next 3 days
        }

    def _process_forecast_to_daily(self, forecast_data: Dict[str, Any]) -> list:
        """
        Convert 3-hour forecast data into daily summaries
        """
        daily_data = {}
        
        for item in forecast_data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            
            if date not in daily_data:
                daily_data[date] = {
                    'date': date,
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'condition': item['weather'][0]['main'],
                    'description': item['weather'][0]['description']
                }
            else:
                # Update min and max temperatures
                daily_data[date]['temp_min'] = min(daily_data[date]['temp_min'], item['main']['temp_min'])
                daily_data[date]['temp_max'] = max(daily_data[date]['temp_max'], item['main']['temp_max'])
        
        # Convert to list and remove today's date
        daily_list = []
        today = datetime.now().strftime('%Y-%m-%d')
        
        for date, data in daily_data.items():
            if date != today:  # Exclude today
                daily_list.append(data)
        
        return daily_list