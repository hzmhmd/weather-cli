import argparse
import sys
# Change from relative to absolute imports
from src.weather_service import WeatherService
from src.exceptions import WeatherAppError, ConfigurationError

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
    """
    city = weather_data['city']
    country = weather_data['country']
    current = weather_data['current']
    
    # Weather condition emoji mapping
    weather_emojis = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️',
        'Smoke': '💨',
        'Haze': '🌫️'
    }
    
    output = []
    output.append(f"🌍 Weather for {city}, {country}")
    output.append("─" * 50)
    
    if current:
        main_data = current.get('main', {})
        weather_info = current.get('weather', [{}])[0]
        
        # Temperature and conditions
        current_temp = main_data.get('temp', 'N/A')
        feels_like = main_data.get('feels_like', 'N/A')
        condition = weather_info.get('main', 'N/A')
        description = weather_info.get('description', 'N/A')
        emoji = weather_emojis.get(condition, '🌈')
        
        output.append(f"🌡️  Temperature: {current_temp:.1f}°C (Feels like {feels_like:.1f}°C)")
        output.append(f"🌈 Conditions: {emoji} {description.title()}")
        output.append("")
        
        # Additional weather details
        humidity = main_data.get('humidity', 'N/A')
        pressure = main_data.get('pressure', 'N/A')
        wind_speed = current.get('wind', {}).get('speed', 'N/A')
        visibility = current.get('visibility', 'N/A')
        
        output.append("📊 Additional Details:")
        output.append(f"   💧 Humidity: {humidity}%")
        output.append(f"   📊 Pressure: {pressure} hPa")
        output.append(f"   💨 Wind Speed: {wind_speed} m/s")
        if visibility != 'N/A':
            output.append(f"   👁️  Visibility: {visibility/1000:.1f} km")
        else:
            output.append(f"   👁️  Visibility: {visibility}")
    
    return "\n".join(output)

def main():
    """Main CLI entry point"""
    try:
        args = parse_arguments()
        
        # Initialize weather service
        weather_service = WeatherService()
        
        # Get weather data
        weather_data = weather_service.get_weather_data(args.city, args.country)
        
        # Format and display output
        print(format_weather_output(weather_data))
        
    except WeatherAppError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()