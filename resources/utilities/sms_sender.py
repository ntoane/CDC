import os
import requests
import json
from resources.static.response_templates import INPUT_INCOMPLETE, EXECUTION_SUCCESS, EXECUTION_FAIL

class SMS:
    def __init__(self):
        # Check if we're in simulation mode (no actual SMS sent)
        # self.simulation_mode = os.environ.get('SMS_SIMULATION_MODE', 'false').lower() == 'true'
        self.simulation_mode = True  # For testing purposes, always in simulation mode

    def send_sms(self, msisdn, message):  
        if self.simulation_mode:
            return {'success': True, 'simulated': True, 'message_id': 'simulation-0000'}
        
        url=os.environ["SMS_ENGINE_ENDPOINT"]
        payload = json.dumps({
        "msisdn": msisdn,
        "message": message
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url=url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            return EXECUTION_SUCCESS
        EXECUTION_FAIL["data"]["message"] = "SMS API integration unsuccessful: Get SMS"
        return EXECUTION_FAIL