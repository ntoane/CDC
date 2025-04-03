"""
Manage ussd_session:
Process requests and provide responses
"""
import os
# custom
from models.ussd_session import USSDSession
from models.ussd_session import USSDSessionState
from resources.static.response_templates import REQUEST_INPUT_INCOMPLETE, APPLICATION_ERRORED, SERVICE_NOT_ALLOWED
from resources.utilities.request_handler import XMLRequestParser
from resources.utilities.response_handler import XMLResponseBuilder
from controllers.integration.vxview.systemapi import SystemAPIIntegrationController
import logging

from models.cdc_transactions import CDCTransactions

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logger for SMS service
ussd_logger = logging.getLogger('USSD')
ussd_logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(os.path.join(log_dir, 'ussd_session.log'))
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
ussd_logger.addHandler(file_handler)

class USSDSessionController:
    def __init__(self, request_data: bytes = None):
        super().__init__()

        if request_data:
            __request = XMLRequestParser(xml_post_data=request_data)
            self.__request_data = __request.get_request_data()
            
        self.logger = ussd_logger

    def process_request(self):
        # check if ussd_session exists
        # process request
        # get response ussd_session_state

        if not self.__request_data:
            self.logger.error("Request data is None")
            return REQUEST_INPUT_INCOMPLETE

        # get subscriber tariff type

        __tariff_type = SystemAPIIntegrationController(msisdn=self.__request_data["msisdn"]).get_tariff_type()
        print(f"Tarrif Type: {__tariff_type}")
        
        if not __tariff_type["success"]:
            
            # operation failed
            self.logger.error(f"Failed to get tariff type: {__tariff_type['data']['message']}")
            __response_xml = XMLResponseBuilder(session_id=self.__request_data["session_id"],
                                                response_type=3,
                                                message=APPLICATION_ERRORED["data"]["message"])
            return __response_xml.get_response_body()

        if __tariff_type['data']['tariff_type'] != "Prepaid":
            self.logger.error(f"Service not allowed for {__tariff_type['data']['tariff_type']} users")
            __response_xml = XMLResponseBuilder(session_id=self.__request_data["session_id"],
                                                response_type=3,
                                                message=SERVICE_NOT_ALLOWED['data']['message'])
            return __response_xml.get_response_body()
        # create ussd_session instance
        __session = USSDSession(session_uid=self.__request_data["session_id"], msisdn=self.__request_data["msisdn"],
                                user_input=self.__request_data["request_input"])
        print(f"__Session Data: {__session.__dict__}")
        
        # register new ussd_session
        if self.__request_data["request_type"] == "1":
            self.logger.info("=" * 80)  # Creates a line of 50 equal signs
            self.logger.info(f"New session request from {self.__request_data['msisdn']} with session id {self.__request_data['session_id']}")
            return self.handle_new_session(__session)

        # active ussd_session
        # TODO: 2. perform tasks [CRUD], 3. update state, 4. respond
        elif self.__request_data["request_phase"] == "2":
            return self.handle_active_session(__session)

        else:
            # operation failed
            __failure_message = APPLICATION_ERRORED["data"]["message"]
            __response_xml = XMLResponseBuilder(session_id=self.__request_data["session_id"],
                                                response_type=3,
                                                message=__failure_message)
            return __response_xml.get_response_body()


    def handle_new_session(self, session:USSDSession):
        if session.initialize()["success"]:
            __next_state = session.get_next_state()

            if __next_state["success"]:
                # ussd_string = self.__request_data["request_input"]
                
                # gather inputs
                msisdn = self.__request_data["msisdn"]
                response_message = __next_state["data"]["next_state_message"]
                __input_required = True if __next_state["data"]["next_state_input_required"] == "Y" else False

                __response_xml = XMLResponseBuilder(session_id=__next_state["data"]["session_uid"],
                                                    response_type=2 if __input_required else 3,
                                                    message=response_message)
                
                # update current state in ussd_session to next state
                __set_next_state = session.set_next_state(next_state=__next_state["data"]["next_state"],
                                                          next_state_alias=__next_state["data"]["next_state_alias"],
                                                          next_state_phase=__next_state["data"]["next_state_phase"])
                if __set_next_state["success"]:
                    self.logger.info(f"Successfully set next state for session {session.session_uid}")
                    return __response_xml.get_response_body()
                self.logger.error(f"Failed to set next state for session {session.session_uid}")

        # operation failed
        __failure_message = APPLICATION_ERRORED["data"]["message"]
        __response_xml = XMLResponseBuilder(session_id=self.__request_data["session_id"],
                                            response_type=3,
                                            message=APPLICATION_ERRORED["data"]["message"])
        self.logger.error(f"Failed to initialize session {session.session_uid}")
        return __response_xml.get_response_body()
    
    
    def handle_active_session(self, session:USSDSession):        
        # get next state
        __next_state = session.get_next_state()
        print(f"NEXT STATE: \n{__next_state}")

        # get next state operation failed
        if not __next_state["success"]:
            __response_xml = XMLResponseBuilder(session_id=self.__request_data["session_id"],
                                                response_type=3,
                                                message=APPLICATION_ERRORED["data"]["message"])
            self.logger.error(f"Failed to get next state for session {session.session_uid}")
            return __response_xml.get_response_body()

        # gather inputs
        __input_required = True if __next_state["data"]["next_state_input_required"] == "Y" else False
        response_message = __next_state["data"]["next_state_message"]

        # Add logic for things to do before responding to customer / next state
        # 1. Logic for Airtime transfer
        if self.__request_data["request_input"] == "1":
            airtime_transfers = CDCTransactions().get_airtime_transfers(self.__request_data["msisdn"])
            result = CDCTransactions().send_sms(self.__request_data["msisdn"], "AIRTIME TRANSFERS: ", airtime_transfers)
            if not result["success"]:
                self.logger.error(f"Failed to send SMS for airtime transfers to {self.__request_data['msisdn']}, with session id {session.session_uid}, message: {result['message']}")
                response_message = result['message']
            self.logger.info(f"Successfully sent SMS for airtime transfers to {self.__request_data['msisdn']}, with session id {session.session_uid}")
                
        # 2. Logic for Bundle purchase
        elif self.__request_data["request_input"] == "2":
            bundle_purchases = CDCTransactions().get_bundle_purchases(self.__request_data["msisdn"])
            result = CDCTransactions().send_sms(self.__request_data["msisdn"], "BUNDLE PURCHASE: ", bundle_purchases)
            if not result["success"]:
                self.logger.error(f"Failed to send SMS for bundle purchases to {self.__request_data['msisdn']}, with session id {session.session_uid}, message: {result['message']}")
                response_message = result['message']
            self.logger.info(f"Successfully sent SMS for bundle purchases to {self.__request_data['msisdn']}, with session id {session.session_uid}")
                 
        # 3. Logic for Call data records
        elif self.__request_data["request_input"] == "3":
            call_records = CDCTransactions().get_call_records(self.__request_data["msisdn"])
            result = CDCTransactions().send_sms(self.__request_data["msisdn"], "CALL RECORDS: ", call_records)
            if not result["success"]:
                self.logger.error(f"Failed to send SMS for call records to {self.__request_data['msisdn']}, with session id {session.session_uid}, message: {result['message']}")
                response_message = result['message']
            self.logger.info(f"Successfully sent SMS for call records to {self.__request_data['msisdn']}, with session id {session.session_uid}")
                        
        
        # Ensure proper error handling
        __input_required = False if "could not be processed" in response_message else __input_required

        # build response body
        __response_xml = XMLResponseBuilder(session_id=__next_state["data"]["session_uid"],
                                                    response_type=2 if __input_required else 3,
                                                    message=response_message)

        # update current state in ussd_session to next state
        __set_next_state = session.set_next_state(next_state=__next_state["data"]["next_state"],
                                                    next_state_alias=__next_state["data"][
                                                        "next_state_alias"],
                                                    next_state_phase=__next_state["data"][
                                                        "next_state_phase"])
        if __set_next_state["success"]:
            return __response_xml.get_response_body()
        


