import pytest
import os
import sys
from unittest.mock import patch, Mock

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Use absolute imports
from src.weather_service import WeatherService
from src.exceptions import ConfigurationError, GeoCodingError, WeatherAPIError, NetworkError

class TestWeatherService:
    """Test cases for WeatherService class"""
    
    def test_missing_api_key(self):
        """Test that ConfigurationError is raised when API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError, match="OPENWEATHER_API_KEY environment variable is not set"):
                WeatherService()
    
    def test_valid_initialization(self):
        """Test successful initialization with API key"""
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            assert service.api_key == 'test-key'
    
    @patch('src.weather_service.requests.get')
    def test_get_coordinates_success(self, mock_get):
        """Test successful coordinate lookup - MOCKED"""
        # Mock response for geocoding API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'name': 'Puchong', 'lat': 3.0000, 'lon': 101.0000, 'country': 'MY'}
        ]
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            lat, lon = service.get_coordinates('Puchong', 'MY')
            
            assert lat == 3.0000
            assert lon == 101.0000
            
            # Verify API was called with correct parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "http://api.openweathermap.org/geo/1.0/direct"
            assert call_args[1]['params']['q'] == "Puchong,MY"
    
    @patch('src.weather_service.requests.get')
    def test_get_coordinates_city_not_found(self, mock_get):
        """Test GeoCodingError when city is not found - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []  # Empty response means city not found
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            
            # Check for the exception type rather than exact message
            with pytest.raises(GeoCodingError):
                service.get_coordinates('UnknownCity', 'XX')
    
    @patch('src.weather_service.requests.get')
    def test_get_coordinates_network_error(self, mock_get):
        """Test NetworkError when there's a connection issue - MOCKED"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            
            # Check for the exception type
            with pytest.raises(NetworkError):
                service.get_coordinates('Puchong', 'MY')
    
    @patch('src.weather_service.requests.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful current weather retrieval - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coord': {'lon': 101.0000, 'lat': 3.0000},
            'weather': [{'id': 801, 'main': 'Clouds', 'description': 'few clouds', 'icon': '02d'}],
            'main': {
                'temp': 28.5,
                'feels_like': 30.2,
                'temp_min': 27.0,
                'temp_max': 30.0,
                'pressure': 1013,
                'humidity': 65
            },
            'wind': {'speed': 3.1, 'deg': 120},
            'visibility': 10000,
            'name': 'Puchong'
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            result = service.get_current_weather(3.0000, 101.0000)
            
            assert 'main' in result
            assert 'weather' in result
            assert result['main']['temp'] == 28.5
            assert result['weather'][0]['main'] == 'Clouds'
            
            # Verify API call
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://api.openweathermap.org/data/2.5/weather"
            assert call_args[1]['params']['lat'] == 3.0000
            assert call_args[1]['params']['lon'] == 101.0000
            assert call_args[1]['params']['units'] == 'metric'
    
    @patch('src.weather_service.requests.get')
    def test_get_current_weather_invalid_api_key(self, mock_get):
        """Test WeatherAPIError for invalid API key - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'invalid-key'}):
            service = WeatherService()
            
            # Check for the exception type
            with pytest.raises(WeatherAPIError):
                service.get_current_weather(3.0000, 101.0000)
    
    @patch('src.weather_service.requests.get')
    def test_get_current_weather_rate_limit(self, mock_get):
        """Test WeatherAPIError for rate limiting - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            
            # Check for the exception type
            with pytest.raises(WeatherAPIError):
                service.get_current_weather(3.0000, 101.0000)
    
    @patch('src.weather_service.requests.get')
    def test_get_weather_data_integration(self, mock_get):
        """Test complete weather data retrieval - MOCKED"""
        # Mock geocoding response
        mock_geocoding_response = Mock()
        mock_geocoding_response.status_code = 200
        mock_geocoding_response.json.return_value = [
            {'name': 'Puchong', 'lat': 3.0000, 'lon': 101.0000, 'country': 'MY'}
        ]
        
        # Mock current weather response
        mock_weather_response = Mock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = {
            'coord': {'lon': 101.0000, 'lat': 3.0000},
            'weather': [{'id': 801, 'main': 'Clouds', 'description': 'few clouds', 'icon': '02d'}],
            'main': {
                'temp': 28.5,
                'feels_like': 30.2,
                'temp_min': 27.0,
                'temp_max': 30.0,
                'pressure': 1013,
                'humidity': 65
            },
            'wind': {'speed': 3.1, 'deg': 120},
            'visibility': 10000,
            'name': 'Puchong'
        }
        
        # Make mock return different responses for different calls
        mock_get.side_effect = [mock_geocoding_response, mock_weather_response]
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            result = service.get_weather_data('Puchong', 'MY')
            
            assert result['city'] == 'Puchong'
            assert result['country'] == 'MY'
            assert result['coordinates']['lat'] == 3.0000
            assert result['coordinates']['lon'] == 101.0000
            assert 'current' in result