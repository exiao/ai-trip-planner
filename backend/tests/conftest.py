"""
Pytest configuration file
"""
import os

# Set testing environment variable when running tests
os.environ["TESTING"] = "1"

# Configure test timeout
def pytest_configure(config):
    config.option.timeout = 5