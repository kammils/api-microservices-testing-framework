"""
Root conftest.py

Pytest configuration and shared fixtures for the entire test suite.
Imports fixtures from src.fixtures.conftest to make them available to all tests.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import all fixtures from src.fixtures.conftest
pytest_plugins = ["src.fixtures.conftest"]
