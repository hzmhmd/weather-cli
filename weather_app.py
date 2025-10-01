#!/usr/bin/env python3
"""
Weather CLI Tool - Get current weather and 3-day forecast for any city worldwide
"""

import os
import sys
import argparse
from src.weather_service import WeatherService
from src.exceptions import WeatherAppError, ConfigurationError


def format_weather_output(weather_data: dict) -> str:
    """
    Format weather data into readable string with 3-day forecast
    """
    city = weather_data['city']
    country = weather_data['country']
    current = weather_data['current']
    daily_forecast = weather_data.get('daily', [])
    
    output = []
    output.append(f"Weather for {city}, {country}")
    output.append("=" * 40)
    
    # Current weather
    if current:
        main_data = current.get('main', {})
        weather_info = current.get('weather', [{}])[0]
        
        current_temp = main_data.get('temp', 'N/A')
        feels_like = main_data.get('feels_like', 'N/A')
        description = weather_info.get('description', 'N/A')
        
        output.append(f"Current: {description.title()} {current_temp:.1f}C (Feels like {feels_like:.1f}C)")
        output.append("")
        
        # Additional weather details
        humidity = main_data.get('humidity', 'N/A')
        pressure = main_data.get('pressure', 'N/A')
        wind_speed = current.get('wind', {}).get('speed', 'N/A')
        
        output.append("Additional Details:")
        output.append(f"  Humidity: {humidity}%")
        output.append(f"  Pressure: {pressure} hPa")
        output.append(f"  Wind Speed: {wind_speed} m/s")
        output.append("")
    
    # 3-Day Forecast
    if daily_forecast:
        output.append("3-Day Forecast:")
        output.append("-" * 40)
        
        for day in daily_forecast:
            date = day['date']
            max_temp = day['temp_max']
            min_temp = day['temp_min']
            condition = day['description']
            
            output.append(f"{date}: {condition.title()}")
            output.append(f"  Max: {max_temp:.1f}C, Min: {min_temp:.1f}C")
            output.append("")
    
    return "\n".join(output)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Get current weather and 3-day forecast for any city worldwide',
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