import os
import base64
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logger for SMS service
sms_logger = logging.getLogger('sms_service')
sms_logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(os.path.join(log_dir, 'sms.log'))
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
sms_logger.addHandler(file_handler)

class SMSService:
    """Service for sending SMS messages using BulkSMS API with token authentication"""
    
    def __init__(self):
        """Initialize SMS service with configuration from environment variables"""
        self.token_id = os.environ.get('BULKSMS_TOKEN_ID')
        self.token_secret = os.environ.get('BULKSMS_TOKEN_SECRET')
        self.api_url = os.environ.get('BULKSMS_API_URL')
        # Check if we're in simulation mode (no actual SMS sent)
        # self.simulation_mode = os.environ.get('SMS_SIMULATION_MODE', 'false').lower() == 'true'
        self.simulation_mode = True  # For testing purposes, always in simulation mode
        
        # Use the configured logger
        self.logger = sms_logger
        
        if not all([self.token_id, self.token_secret, self.api_url]):
            self.logger.warning("SMS service not fully configured. Check environment variables.")

    def _get_authorization_header(self) -> Dict[str, str]:
        """
        Generate the Authorization header with Basic auth encoding
        
        Returns:
            Dict containing the Authorization header
        """
        if not self.token_id or not self.token_secret:
            self.logger.error("Missing BulkSMS token credentials")
            return {}
            
        # Format: token_id:token_secret
        auth_string = f"{self.token_id}:{self.token_secret}"
        # Base64 encode
        encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {encoded}"}

    def send_message(self, to: str, body: str) -> Dict[str, Any]:
        """
        Send an SMS message
        
        Args:
            to: Destination phone number (international format with + prefix)
            body: Message content
            
        Returns:
            Dict with status information
        """
        if self.simulation_mode:
            self.logger.info(f"SIMULATION MODE: Would send SMS to {to}: {body}")
            return {'success': True, 'simulated': True, 'message_id': 'simulation-0000'}
            
        if not all([self.token_id, self.token_secret, self.api_url]):
            return {'success': False, 'error': 'SMS service not configured'}
            
        if not to or not body:
            return {'success': False, 'error': 'Missing recipient or message body'}
        
        # Ensure phone number is in international format
        if not to.startswith('+'):
            to = f"+{to}"
            
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            **self._get_authorization_header()
        }
        
        # Prepare payload
        payload = {
            'to': to,
            'body': body,
            'encoding': 'TEXT',  # Use UNICODE to support all characters
        }
        
        try:
            self.logger.debug(f"Sending SMS to {to}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                result = response.json()
                
                # Handle the list response format from BulkSMS API
                if isinstance(result, list) and result:
                    # Get the first message result (we're sending a single message)
                    message_result = result[0]
                    message_id = message_result.get('id', 'unknown')
                    self.logger.info(f"SMS sent successfully to {to}, ID: {message_id}")
                    
                    return {
                        'success': True,
                        'message_id': message_id,
                        'response': result
                    }
                else:
                    # Fallback for unexpected response format
                    self.logger.info(f"SMS sent successfully to {to}, but couldn't extract ID from response")
                    return {
                        'success': True,
                        'message_id': 'unknown',
                        'response': result
                    }
                
        except Exception as e:
            self.logger.exception(f"Error sending SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
# Create a singleton instance for import
sms_service = SMSService()