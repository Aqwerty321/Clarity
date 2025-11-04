"""
Test configuration
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_user_id():
    """Fixture for test user ID"""
    return "test_user_123"


@pytest.fixture
def sample_text():
    """Fixture for sample text"""
    return """
    Machine learning is a method of data analysis that automates analytical model building.
    It is a branch of artificial intelligence based on the idea that systems can learn from data,
    identify patterns and make decisions with minimal human intervention.
    """
