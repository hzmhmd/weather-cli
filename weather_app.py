#!/usr/bin/env python3
"""
Weather CLI Tool - Get current weather for any city worldwide
"""

import os
import sys
import argparse
import requests
from typing import Dict, Any


class WeatherAppError(Exception):
    pass


class ConfigurationError(WeatherAppError):
    pass


class GeoCodingError(WeatherAppError):
    pass


class WeatherAPIError(WeatherAppError):
    pass


class NetworkError(WeatherAppError):
    pass


class WeatherService:
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


def format_weather_output(weather_data: dict) -> str:
    """
    Format weather data into human-readable string
    """
    city = weather_data['city']
    country = weather_data['country']
    current = weather_data['current']
    
    output = []
    output.append(f"Weather for {city}, {country}")
    output.append("=" * 50)
    
    if current:
        main_data = current.get('main', {})
        weather_info = current.get('weather', [{}])[0]
        
        current_temp = main_data.get('temp', 'N/A')
        feels_like = main_data.get('feels_like', 'N/A')
        description = weather_info.get('description', 'N/A')
        
        output.append(f"Temperature: {current_temp:.1f}C (Feels like {feels_like:.1f}C)")
        output.append(f"Conditions: {description.title()}")
        output.append("")
        
        humidity = main_data.get('humidity', 'N/A')
        pressure = main_data.get('pressure', 'N/A')
        wind_speed = current.get('wind', {}).get('speed', 'N/A')
        visibility = current.get('visibility', 'N/A')
        
        output.append("Additional Details:")
        output.append(f"  Humidity: {humidity}%")
        output.append(f"  Pressure: {pressure} hPa")
        output.append(f"  Wind Speed: {wind_speed} m/s")
        if visibility != 'N/A':
            output.append(f"  Visibility: {visibility/1000:.1f} km")
        else:
            output.append(f"  Visibility: {visibility}")
    
    return "\n".join(output)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Get current weather for any city worldwide',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python weather_app.py --city "London" --country "GB"
  python weather_app.py --city "Tokyo" --country "JP"
  python weather_app.py --city "New York" --country "US"
        """
    )
    
    parser.add_argument(
        '--city',
        type=str,
        required=True,
        help='City name (e.g., "London")'
    )
    
    parser.add_argument(
        '--country',
        type=str,
        required=True,
        help='Two-letter country code (e.g., "GB")'
    )
    
    return parser.parse_args()


def main():
    """Main CLI entry point"""
    try:
        args = parse_arguments()
        
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_data(args.city, args.country)
        
        print(format_weather_output(weather_data))
        
    except WeatherAppError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()