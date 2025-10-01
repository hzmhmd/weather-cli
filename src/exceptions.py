"""
Custom exceptions for the weather CLI application.
"""

class WeatherAppError(Exception):
    """Base exception for weather application errors"""
    pass


class ConfigurationError(WeatherAppError):
    """Raised when there's a configuration issue (e.g., missing API key)"""
    pass


class GeoCodingError(WeatherAppError):
    """Raised when geocoding fails (city not found)"""
    pass


class WeatherAPIError(WeatherAppError):
    """Raised when weather API calls fail"""
    pass


class NetworkError(WeatherAppError):
    """Raised when there are network issues"""
    pass