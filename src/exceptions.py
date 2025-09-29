

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