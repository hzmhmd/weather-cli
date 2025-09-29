import argparse
import sys
from typing import Optional
from .weather_service import WeatherService
from .exceptions import WeatherAppError, ConfigurationError

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Get weather forecast for a city',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python weather_cli.py --city "Puchong" --country "MY"
  python weather_cli.py --city "London" --country "GB"
        """
    )
    
    parser.add_argument(
        '--city',
        type=str,
        required=True,
        help='City name (e.g., "Puchong")'
    )
    
    parser.add_argument(
        '--country',
        type=str,
        required=True,
        help='Two-letter country code (e.g., "MY")'
    )
    
    return parser.parse_args()

def format_weather_output(weather_data: dict) -> str:
    """
    Format weather data into human-readable string
    
    Args:
        weather_data: Weather data dictionary
        
    Returns:
        Formatted string for display
    """
    city = weather_data['city']
    country = weather_data['country']
    current = weather_data['current']
    daily_forecast = weather_data['daily']
    
   
    weather_emojis = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️'
    }
    
    output = []
    output.append(f"Weather for {city}, {country}")
    output.append("─" * 40)
    

    if current:
        current_temp = current.get('temp', 'N/A')
        current_weather = current.get('weather', [{}])[0]
        condition = current_weather.get('main', 'N/A')
        description = current_weather.get('description', 'N/A')
        emoji = weather_emojis.get(condition, '🌈')
        
        output.append(f"Current: {emoji} {description.title()} ({current_temp:.1f}°C)")
        output.append("")
    
  
    output.append("3-Day Forecast:")
    output.append("─" * 40)
    
    for day in daily_forecast:
        timestamp = day.get('dt', 0)
        from datetime import datetime
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        temp = day.get('temp', {})
        max_temp = temp.get('max', 'N/A')
        min_temp = temp.get('min', 'N/A')
        weather = day.get('weather', [{}])[0]
        condition = weather.get('main', 'N/A')
        description = weather.get('description', 'N/A')
        emoji = weather_emojis.get(condition, '🌈')
        
        if isinstance(max_temp, (int, float)) and isinstance(min_temp, (int, float)):
            temp_str = f"Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C"
        else:
            temp_str = "Temperature data unavailable"
        
        output.append(f"{date_str}: {emoji} {description.title()} ({temp_str})")
    
    return "\n".join(output)

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