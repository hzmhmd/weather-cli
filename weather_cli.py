#!/usr/bin/env python3
"""
Weather CLI Tool
A command-line interface to get weather forecasts using OpenWeatherMap API
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli import main

if __name__ == '__main__':
    main()