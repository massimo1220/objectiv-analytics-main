"""
Copyright 2021 Objectiv B.V.
"""
from importlib.resources import read_text


# The version is defined in a file called VERSION that only contains the version string
__version__ = read_text(package='objectiv_backend', resource='VERSION').strip()
