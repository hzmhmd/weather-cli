import pytest
import os
from unittest.mock import patch, Mock
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
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "http://api.openweathermap.org/geo/1.0/direct"
            assert call_args[1]['params']['q'] == "Puchong,MY"
    
    @patch('src.weather_service.requests.get')
    def test_get_coordinates_city_not_found(self, mock_get):
        """Test GeoCodingError when city is not found - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []  
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            
            with pytest.raises(GeoCodingError, match="City 'UnknownCity' in country 'XX' not found"):
                service.get_coordinates('UnknownCity', 'XX')
    
    @patch('src.weather_service.requests.get')
    def test_get_coordinates_network_error(self, mock_get):
        """Test NetworkError when there's a connection issue - MOCKED"""
        mock_get.side_effect = ConnectionError("Connection failed")
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            
            with pytest.raises(NetworkError, match="Network error: Unable to connect to weather service"):
                service.get_coordinates('Puchong', 'MY')
    
    @patch('src.weather_service.requests.get')
    def test_get_weather_forecast_success(self, mock_get):
        """Test successful weather forecast retrieval - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'current': {
                'dt': 1672531200,
                'temp': 28.5,
                'weather': [{'main': 'Clear', 'description': 'clear sky'}]
            },
            'daily': [
                {
                    'dt': 1672531200,
                    'temp': {'min': 25.0, 'max': 30.0},
                    'weather': [{'main': 'Clear', 'description': 'clear sky'}]
                },
                {
                    'dt': 1672617600,
                    'temp': {'min': 24.0, 'max': 29.0},
                    'weather': [{'main': 'Rain', 'description': 'light rain'}]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            result = service.get_weather_forecast(3.0000, 101.0000)
            
            assert 'current' in result
            assert 'daily' in result
            assert len(result['daily']) == 2
            
            # Verify API call
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://api.openweathermap.org/data/3.0/onecall"
            assert call_args[1]['params']['lat'] == 3.0000
            assert call_args[1]['params']['lon'] == 101.0000
            assert call_args[1]['params']['units'] == 'metric'
    
    @patch('src.weather_service.requests.get')
    def test_get_weather_forecast_invalid_api_key(self, mock_get):
        """Test WeatherAPIError for invalid API key - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'invalid-key'}):
            service = WeatherService()
            
            with pytest.raises(WeatherAPIError, match="Invalid API key"):
                service.get_weather_forecast(3.0000, 101.0000)
    
    @patch('src.weather_service.requests.get')
    def test_get_weather_forecast_rate_limit(self, mock_get):
        """Test WeatherAPIError for rate limiting - MOCKED"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            
            with pytest.raises(WeatherAPIError, match="API rate limit exceeded"):
                service.get_weather_forecast(3.0000, 101.0000)
    
    @patch('src.weather_service.requests.get')
    def test_get_weather_data_integration(self, mock_get):
        """Test complete weather data retrieval - MOCKED"""
        
        mock_geocoding_response = Mock()
        mock_geocoding_response.status_code = 200
        mock_geocoding_response.json.return_value = [
            {'name': 'Puchong', 'lat': 3.0000, 'lon': 101.0000, 'country': 'MY'}
        ]
        
        mock_weather_response = Mock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = {
            'current': {
                'dt': 1672531200,
                'temp': 28.5,
                'weather': [{'main': 'Clear', 'description': 'clear sky'}]
            },
            'daily': [
                {
                    'dt': 1672531200,
                    'temp': {'min': 25.0, 'max': 30.0},
                    'weather': [{'main': 'Clear', 'description': 'clear sky'}]
                },
                {
                    'dt': 1672617600,
                    'temp': {'min': 24.0, 'max': 29.0},
                    'weather': [{'main': 'Rain', 'description': 'light rain'}]
                }
            ]
        }
        
        mock_get.side_effect = [mock_geocoding_response, mock_weather_response]
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-key'}):
            service = WeatherService()
            result = service.get_weather_data('Puchong', 'MY')
            
            assert result['city'] == 'Puchong'
            assert result['country'] == 'MY'
            assert result['coordinates']['lat'] == 3.0000
            assert result['coordinates']['lon'] == 101.0000
            assert 'current' in result
            assert 'daily' in result
            assert len(result['daily']) == 2