import pytest
import sys
import os
import config
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the os.environ to simulate environment variables for testing
# os.environ["EXADATA_DB_USERNAME"] = "test_user"
# Mock the dotenv module
# mock_dotenv = MagicMock()
# mock_dotenv.load_dotenv = MagicMock()
# sys.modules['dotenv'] = mock_dotenv

# # Mock oracledb before any imports
# mock_oracledb = MagicMock()
# sys.modules['oracledb'] = mock_oracledb

# Now it's safe to import application modules
from views import create_app


@pytest.fixture(scope='session')
def test_client():
    app = create_app()
    
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['DEBUG'] = False

    # Create a test client using the Flask application configured for testing
    with app.test_client() as client:
        # Establish an application context
        with app.app_context():
            yield client  # this is where the testing happens!


@pytest.fixture(scope='function')
def request_payload(request):
    """Configure XML payload to send to the application during testing"""
    __payload = f"<msg> \
        <msisdn>{request.param['msisdn']}</msisdn> \
        <sessionid>{request.param['session_id']}</sessionid> \
        <phase>{str(request.param['phase'])}</phase> \
        <request type='{str(request.param['request_type'])}'>{request.param['user_input']}</request> \
    </msg>"
    return __payload


@pytest.fixture(name="headers", scope="module")
def get_headers():
    """
    Prepare headers to attach to requests
    :return: dict
    """
    return {
        "Content-Type": "application/xml"
    }


@pytest.fixture(name="ussd_endpoint", scope="module")
def get_ussd_endpoint():
    """
    USSD application endpoint
    :return:
    """
    return "/"


@pytest.fixture(name="health_check_endpoint", scope="module")
def get_health_check_endpoint():
    """USSD Health check endpoints"""
    return "/health"
