import pytest
import os
# from dotenv import load_dotenv
import oracledb

@pytest.fixture(scope="module")
def db_connection():
    """Create a database connection for testing"""
    # Load environment variables
    # load_dotenv()
    
    # Get connection details
    user = os.environ.get("DATABASE_USERNAME")
    dsn = os.environ.get("DATABASE_TNS_NAME")
    pw = os.environ.get("DATABASE_PASSWORD")
    wallet_pw = os.environ.get("DATABASE_WALLET_PASSWORD")
    wallet_dir = os.environ.get("DATABASE_WALLET_DIR")
    
    print(f"Connecting as user: {user}")
    print(f"Using TNS name: {dsn}")
    print(f"Wallet directory: {wallet_dir}")
    
    # Connect to the database
    con = oracledb.connect(
        user=user, 
        password=pw, 
        dsn=dsn,
        config_dir=wallet_dir,
        wallet_location=wallet_dir, 
        wallet_password=wallet_pw
    )
    
    yield con
    
    # Teardown - close connection
    con.close()
    print("\nConnection closed")

def test_database_connection(db_connection):
    """Test that we can connect to the database"""
    assert db_connection is not None
    # Verify connection is active by getting version
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM v$version")
    version = cursor.fetchone()
    cursor.close()
    
    assert version is not None
    print(f"\nConnected to Oracle Database: {version[0]}")