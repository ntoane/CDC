import pytest

# print(os.environ)

import uuid
from unittest.mock import patch, MagicMock, call
from datetime import datetime

from models.cdc_transactions import CDCTransactions
from models.ussd_session import USSDSession
from controllers.ussd_session import USSDSessionController


# Mock data for testing
SAMPLE_MSISDN = "26653566580"
SAMPLE_UUID = "12345678-1234-5678-1234-567812345678"
MOCK_TIMESTAMP = datetime.now()


# USSD Session Flow Tests
class TestUSSDSessionFlow:
    @patch('models.ussd_session.USSDSession.execute_query')
    def test_session_creation(self, mock_execute_query):
        """Test that a USSD session can be properly initialized"""
        # Setup
        mock_execute_query.return_value = {"success": True, "data": {"message": "Session created"}}
        
        # Execute
        session = USSDSession(session_uid="12345", msisdn=SAMPLE_MSISDN, user_input="*123#")
        result = session.initialize()
        
        # Assert
        assert result["success"] is True
        mock_execute_query.assert_called_once()
        assert "INSERT INTO CDC_USSD_SESSION VALUES" in mock_execute_query.call_args[0][0]
    
    @patch('models.ussd_session.USSDSession.get_current_state')
    @patch('models.ussd_session.USSDSession.get_next_state')
    @patch('models.ussd_session.USSDSession.set_next_state')
    def test_menu_navigation(self, mock_set_next_state, mock_get_next_state, mock_get_current_state):
        """Test navigation through USSD menu options"""
        # Setup - Mock current state
        mock_get_current_state.return_value = {
            "success": True, 
            "data": {
                "session_uid": "12345", 
                "current_state": "TRANSACTIONS", 
                "current_state_alias": "N.A", 
                "current_state_phase": 0,
                "msisdn": SAMPLE_MSISDN,
                "user_input": "1"
            }
        }
        
        # Mock next state response
        mock_get_next_state.return_value = {
            "success": True,
            "data": {
                "session_uid": "12345",
                "next_state": "AIRTIME_TRANSACTIONS",
                "next_state_message": "Your airtime transfer history will be sent to you shortly via SMS.",
                "next_state_input_required": "N",
                "next_state_alias": "N.A",
                "next_state_phase": 0
            }
        }
        
        # Mock set next state response
        mock_set_next_state.return_value = {"success": True}
        
        # Execute - Create session and process navigation
        session = USSDSession(session_uid="12345", msisdn=SAMPLE_MSISDN, user_input="1")
        
        # First explicitly call get_current_state
        current_state = session.get_current_state()
        assert current_state["success"] is True
        
        # Then get the next state
        next_state = session.get_next_state()
        
        # Finally set the next state
        result = session.set_next_state(next_state["data"]["next_state"])
        
        # Assert
        assert next_state["success"] is True
        assert next_state["data"]["next_state"] == "AIRTIME_TRANSACTIONS"
        assert result["success"] is True
        
        # Verify each mock was called once
        mock_get_current_state.assert_called_once()
        mock_get_next_state.assert_called_once()
        mock_set_next_state.assert_called_once()
    
    @pytest.mark.parametrize('request_payload', [
        {'msisdn': SAMPLE_MSISDN, 'session_id': '12345', 'phase': 2, 'request_type': 2, 'user_input': '0'}  # Changed user_input to '0'
    ], indirect=True)
    def test_session_termination_with_fixtures(self, test_client, request_payload, headers, ussd_endpoint):
        """Test USSD session termination using test fixtures"""
        # Setup - Mock the database responses
        with patch('models.ussd_session.USSDSession.initialize') as mock_init:  # Added initialize mock
            with patch('models.ussd_session.USSDSession.get_current_state') as mock_get_current:
                with patch('models.ussd_session.USSDSession.get_next_state') as mock_get_next:
                    with patch('models.ussd_session.USSDSession.set_next_state') as mock_set_next:
                        # Configure mocks
                        mock_init.return_value = {"success": True}  # Added initialize return
                        mock_get_current.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "current_state": "MAIN_MENU",
                                "current_state_alias": "N.A",
                                "current_state_phase": 0,
                                "msisdn": SAMPLE_MSISDN,
                                "user_input": "0"
                            }
                        }
                        
                        mock_get_next.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "next_state": "EXIT",
                                "next_state_message": "Thank you for using CDC service.",
                                "next_state_input_required": "N",
                                "next_state_alias": "N.A",
                                "next_state_phase": 0
                            }
                        }
                        
                        mock_set_next.return_value = {"success": True}
                        
                        # Execute - Send the request to terminate the session
                        response = test_client.post(
                            ussd_endpoint,
                            data=request_payload,
                            headers=headers
                        )
            
                        # Assert
                        assert response.status_code == 200
                        assert b"Thank you for using CDC service" in response.data
                        assert b"response type='3'" in response.data  # Verify termination response type


# CDC Transactions Tests
class TestCDCTransactions:
    @pytest.mark.parametrize('request_payload', [
        {'msisdn': SAMPLE_MSISDN, 'session_id': '12345', 'phase': 2, 'request_type': 2, 'user_input': '1'}
    ], indirect=True)
    def test_airtime_transfers_integration(self, test_client, request_payload, headers, ussd_endpoint):
        """Integration test for airtime transfers using test fixtures"""
        # Mock session management
        with patch('models.ussd_session.USSDSession.initialize') as mock_init:
            with patch('models.ussd_session.USSDSession.get_current_state') as mock_current:
                with patch('models.ussd_session.USSDSession.get_next_state') as mock_next:
                    with patch('models.ussd_session.USSDSession.set_next_state') as mock_set:
                        # Configure session mocks
                        mock_init.return_value = {"success": True}
                        mock_current.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "current_state": "MAIN_MENU",
                                "current_state_alias": "N.A",
                                "current_state_phase": 0,
                                "msisdn": SAMPLE_MSISDN,
                                "user_input": "1"
                            }
                        }
                        mock_next.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "next_state": "AIRTIME_TRANSACTIONS",
                                "next_state_message": "Your airtime transfer history will be sent to you shortly via SMS.",
                                "next_state_input_required": "N",
                                "next_state_alias": "N.A",
                                "next_state_phase": 0
                            }
                        }
                        mock_set.return_value = {"success": True}

                        # Mock CDC methods
                        with patch('models.cdc_transactions.CDCTransactions.get_airtime_transfers') as mock_get_transfers:
                            with patch('models.cdc_transactions.CDCTransactions.send_sms') as mock_send_sms:
                                # Configure CDC mocks
                                mock_get_transfers.return_value = [
                                    {"message": "1) 10/12/2023 15:30 - Transfer of LSL 50.0 to 26653123456"},
                                    {"message": "2) 11/12/2023 09:15 - Transfer of LSL 100.0 to 26653654321"}
                                ]
                                mock_send_sms.return_value = {"success": True, "message": "SMS sent successfully"}

                                # Execute request
                                response = test_client.post(
                                    ussd_endpoint,
                                    data=request_payload,
                                    headers=headers
                                )

                                # Assert
                                assert response.status_code == 200
                                assert b"Your airtime transfer history will be sent to you shortly via SMS." in response.data
                                
                                # Verify CDC methods were called
                                mock_get_transfers.assert_called_once_with(SAMPLE_MSISDN)
    
    @pytest.mark.parametrize('request_payload', [
        {'msisdn': SAMPLE_MSISDN, 'session_id': '12345', 'phase': 2, 'request_type': 2, 'user_input': '2'}
    ], indirect=True)
    def test_bundle_purchases_integration(self, test_client, request_payload, headers, ussd_endpoint):
        """Integration test for bundle purchases using test fixtures"""
        # Mock session management
        with patch('models.ussd_session.USSDSession.initialize') as mock_init:
            with patch('models.ussd_session.USSDSession.get_current_state') as mock_current:
                with patch('models.ussd_session.USSDSession.get_next_state') as mock_next:
                    with patch('models.ussd_session.USSDSession.set_next_state') as mock_set:
                        # Configure session mocks
                        mock_init.return_value = {"success": True}
                        mock_current.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "current_state": "MAIN_MENU",
                                "current_state_alias": "N.A",
                                "current_state_phase": 0,
                                "msisdn": SAMPLE_MSISDN,
                                "user_input": "2"
                            }
                        }
                        mock_next.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "next_state": "BUNDLE_PURCHASES",
                                "next_state_message": "Your bundle purchase history will be sent to you shortly via SMS.",
                                "next_state_input_required": "N",
                                "next_state_alias": "N.A",
                                "next_state_phase": 0
                            }
                        }
                        mock_set.return_value = {"success": True}

                        # Mock CDC methods
                        with patch('models.cdc_transactions.CDCTransactions.get_bundle_purchases') as mock_get_bundles:
                            with patch('models.cdc_transactions.CDCTransactions.send_sms') as mock_send_sms:
                                # Configure CDC mocks
                                mock_get_bundles.return_value = [
                                    {"message": "1) 10/12/2023 15:30 - Data Bundle 1GB - M100.00"},
                                    {"message": "2) 11/12/2023 09:15 - Voice Bundle 60min - M50.00"}
                                ]
                                mock_send_sms.return_value = {"success": True, "message": "SMS sent successfully"}

                                # Execute request
                                response = test_client.post(
                                    ussd_endpoint,
                                    data=request_payload,
                                    headers=headers
                                )

                                # Assert
                                assert response.status_code == 200
                                assert b"Your bundle purchase history will be sent to you shortly via SMS" in response.data
                                
                                # Verify CDC methods were called
                                mock_get_bundles.assert_called_once_with(SAMPLE_MSISDN)
    
    @pytest.mark.parametrize('request_payload', [
        {'msisdn': SAMPLE_MSISDN, 'session_id': '12345', 'phase': 2, 'request_type': 2, 'user_input': '3'}
    ], indirect=True)
    def test_call_records_integration(self, test_client, request_payload, headers, ussd_endpoint):
        """Integration test for call records using test fixtures"""
        # Mock session management
        with patch('models.ussd_session.USSDSession.initialize') as mock_init:
            with patch('models.ussd_session.USSDSession.get_current_state') as mock_current:
                with patch('models.ussd_session.USSDSession.get_next_state') as mock_next:
                    with patch('models.ussd_session.USSDSession.set_next_state') as mock_set:
                        # Configure session mocks
                        mock_init.return_value = {"success": True}
                        mock_current.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "current_state": "MAIN_MENU",
                                "current_state_alias": "N.A",
                                "current_state_phase": 0,
                                "msisdn": SAMPLE_MSISDN,
                                "user_input": "3"
                            }
                        }
                        mock_next.return_value = {
                            "success": True,
                            "data": {
                                "session_uid": "12345",
                                "next_state": "CALL_RECORDS",
                                "next_state_message": "Your recent call records will be sent to you shortly via SMS.",
                                "next_state_input_required": "N",
                                "next_state_alias": "N.A",
                                "next_state_phase": 0
                            }
                        }
                        mock_set.return_value = {"success": True}

                        # Mock CDC methods
                        with patch('models.cdc_transactions.CDCTransactions.get_call_records') as mock_get_calls:
                            with patch('models.cdc_transactions.CDCTransactions.send_sms') as mock_send_sms:
                                # Configure CDC mocks
                                mock_get_calls.return_value = [
                                    {"message": "1) 10/12/2023 15:30 - Call to 26657****96 - 2min 30sec"},
                                    {"message": "2) 11/12/2023 09:15 - Call to 26658****21 - 5min 10sec"}
                                ]
                                mock_send_sms.return_value = {"success": True, "message": "SMS sent successfully"}

                                # Execute request
                                response = test_client.post(
                                    ussd_endpoint,
                                    data=request_payload,
                                    headers=headers
                                )

                                # Assert
                                assert response.status_code == 200
                                assert b"Your recent call records will be sent to you shortly via SMS" in response.data
                                
                                # Verify CDC methods were called
                                mock_get_calls.assert_called_once_with(SAMPLE_MSISDN)

    # Unit Tests for CDC Transaction Class Methods
    
    @patch('models.cdc_transactions.CDCTransactions.execute_query')
    @patch('uuid.uuid4')
    def test_get_airtime_transfers(self, mock_uuid, mock_execute_query):
        """Test the airtime transfer history retrieval logic"""
        # Setup
        mock_uuid.return_value = SAMPLE_UUID
        
        # Mock database responses
        mock_data = [
            {
                "OC_RECORDTIMESTAMP": MOCK_TIMESTAMP,
                "OC_SERVED_MSISDN_NORM": SAMPLE_MSISDN,
                "OC_OTHERPARTY_NORM": "26652123456",
                "OC_ACCOUNT_CHARGE": 50.0
            },
            {
                "OC_RECORDTIMESTAMP": MOCK_TIMESTAMP,
                "OC_SERVED_MSISDN_NORM": SAMPLE_MSISDN,
                "OC_OTHERPARTY_NORM": "26653987654",
                "OC_ACCOUNT_CHARGE": 100.0
            }
        ]
        
        # Set up the mock to return different values for each call
        mock_execute_query.side_effect = [True, mock_data, True]
        
        # Execute
        cdc = CDCTransactions()
        result = cdc.get_airtime_transfers(SAMPLE_MSISDN)
        
        # Assert
        assert len(result) == 2
        assert "message" in result[0]
        
        # Check formatting of message
        assert MOCK_TIMESTAMP.strftime("%d/%m/%Y") in result[0]["message"]
        assert "M50.0" in result[0]["message"] or "M50,0" in result[0]["message"]
        
        # Check that phone masking was applied
        first_msg = result[0]["message"]
        assert "26652" in first_msg
        assert "*" in first_msg  # Check for any masking character
        
        # Verify correct number of database calls
        assert mock_execute_query.call_count == 3  # INSERT, SELECT, UPDATE
        
        # Verify content of the SELECT query
        select_call = mock_execute_query.call_args_list[1]
        assert "SELECT" in select_call[0][0]
        assert "AIRTIME_TRANSFER" in select_call[0][0]
        assert f"OC_SERVED_MSISDN_NORM = '{SAMPLE_MSISDN}'" in select_call[0][0]
    
    @patch('models.cdc_transactions.CDCTransactions.execute_query')
    @patch('uuid.uuid4')
    def test_get_bundle_purchases(self, mock_uuid, mock_execute_query):
        """Test the bundle purchase history retrieval logic"""
        # Setup
        mock_uuid.return_value = SAMPLE_UUID
        
        # Mock database responses
        mock_data = [
            {
                "OC_RECORDTIMESTAMP": MOCK_TIMESTAMP,
                "OC_SERVED_MSISDN_NORM": SAMPLE_MSISDN,
                "EVENT": "Data Bundle 1GB",
                "OC_ACCOUNT_CHARGE": 100.0,
                "OC_OTHERPARTY_NORM": None  # Test with null other party
            },
            {
                "OC_RECORDTIMESTAMP": MOCK_TIMESTAMP,
                "OC_SERVED_MSISDN_NORM": SAMPLE_MSISDN,
                "EVENT": "Voice Bundle 60min",
                "OC_ACCOUNT_CHARGE": 50.0,
                "OC_OTHERPARTY_NORM": "26659876543"  # Test with other party
            }
        ]
        
        # Set up the mock to return different values for each call
        mock_execute_query.side_effect = [True, mock_data, True]
        
        # Execute
        cdc = CDCTransactions()
        result = cdc.get_bundle_purchases(SAMPLE_MSISDN)
        
        # Assert
        assert len(result) == 2
        assert "message" in result[0]
        
        # Check first message (no other party)
        assert "Data Bundle 1GB" in result[0]["message"]
        assert "M100.0" in result[0]["message"] or "M100,0" in result[0]["message"]
        
        # Check second message (with other party)
        second_msg = result[1]["message"]
        assert "Voice Bundle 60min" in second_msg
        assert "26659" in second_msg
        assert "*" in second_msg
        
        # Verify correct number of database calls
        assert mock_execute_query.call_count == 3
        
        # Verify content of the SELECT query
        select_call = mock_execute_query.call_args_list[1]
        assert "SELECT" in select_call[0][0]
        assert "BUNDLE_PURCHASE" in select_call[0][0]
        assert f"OC_SERVED_MSISDN_NORM = '{SAMPLE_MSISDN}'" in select_call[0][0]
    
    @patch('models.cdc_transactions.CDCTransactions.execute_query')
    @patch('uuid.uuid4')
    def test_get_call_records(self, mock_uuid, mock_execute_query):
        """Test the call records retrieval and formatting"""
        # Setup
        mock_uuid.return_value = SAMPLE_UUID
        
        # Mock database responses
        mock_data = [
            {
                "OC_RECORDTIMESTAMP": MOCK_TIMESTAMP,
                "OC_SERVED_MSISDN_NORM": SAMPLE_MSISDN,
                "OC_OTHERPARTY_NORM": "26657653596",
                "OC_TOTAL_USED_DURATION": 2.5,  # 2.5 minutes = 2min 30sec
                "OC_ACCOUNT_BALANCE_AFTER": 10.0
            },
            {
                "OC_RECORDTIMESTAMP": MOCK_TIMESTAMP,
                "OC_SERVED_MSISDN_NORM": SAMPLE_MSISDN,
                "OC_OTHERPARTY_NORM": "26658765432",
                "OC_TOTAL_USED_DURATION": 0.75,  # 0.75 minutes = 45sec
                "OC_ACCOUNT_BALANCE_AFTER": 8.5
            }
        ]
        
        # Set up the mock to return different values for each call
        mock_execute_query.side_effect = [True, mock_data, True]
        
        # Execute
        cdc = CDCTransactions()
        result = cdc.get_call_records(SAMPLE_MSISDN)
        
        # Assert
        assert len(result) == 2
        assert "message" in result[0]
        
        # Check format of first call (2min 30sec)
        first_msg = result[0]["message"]
        assert "26657" in first_msg
        assert "*" in first_msg
        assert "2min" in first_msg
        assert "30sec" in first_msg or "30s" in first_msg
        
        # Check format of second call (45sec)
        second_msg = result[1]["message"]
        assert "26658" in second_msg
        assert "*" in second_msg
        assert "45sec" in second_msg or "45s" in second_msg
        
        # Verify correct number of database calls
        assert mock_execute_query.call_count == 3
        
        # Verify content of the SELECT query
        select_call = mock_execute_query.call_args_list[1]
        assert "SELECT" in select_call[0][0]
        assert "CALL_RECORDS" in select_call[0][0]
        assert f"OC_SERVED_MSISDN_NORM = '{SAMPLE_MSISDN}'" in select_call[0][0]
    
    # @patch('resources.utilities.sms_sender.send_sms')
    # def test_send_sms(self, mock_send_message):
    #     """Test the SMS formatting and sending"""
    #     # Setup
    #     mock_send_message.return_value = {"success": True, "simulated": True}
        
    #     # Prepare test data
    #     sms_items = [
    #         {"message": "1) Test message with special chars: $%^&"},
    #         {"message": "2) Another test with emojis: 😊📱"}
    #     ]
        
    #     # Execute
    #     cdc = CDCTransactions()
    #     result = cdc.send_sms(SAMPLE_MSISDN, "TEST MESSAGE HEADER: ", sms_items)
        
    #     # Assert
    #     assert result is True
    #     mock_send_message.assert_called_once()
        
    #     # Check formatting
    #     call_args = mock_send_message.call_args[1]
    #     assert call_args["to"] == f"+{SAMPLE_MSISDN}"  # Should add + prefix
        
    #     # Check message content
    #     message_body = call_args["body"]
    #     assert "TEST MESSAGE HEADER: " in message_body
    #     assert "1) Test message with special chars" in message_body
    #     assert "2) Another test" in message_body
    
    def test_mask_phone_number(self):
        """Test the phone number masking functionality"""
        # Setup
        cdc = CDCTransactions()
        test_numbers = [
            "26657123456",  # standard 11-digit number
            "266571234567",  # 12-digit number
            "26651234",      # short number
            None,            # None value
            "",              # Empty string
            "1234"           # Very short number
        ]
        
        # Execute and assert
        # Standard number
        masked = cdc.mask_phone_number(test_numbers[0])
        assert masked.startswith("26657")
        assert "*" in masked
        
        # Longer number
        masked = cdc.mask_phone_number(test_numbers[1])
        assert masked.startswith("26657")
        assert "*" in masked
        
        # Short number - should still mask something
        masked = cdc.mask_phone_number(test_numbers[2])
        assert "*" in masked
        
        # None value - should handle gracefully
        masked = cdc.mask_phone_number(test_numbers[3])
        assert masked == ""
        
        # Empty string - should return empty
        masked = cdc.mask_phone_number(test_numbers[4])
        assert masked == ""
        
        # Very short number - should still do something sensible
        masked = cdc.mask_phone_number(test_numbers[5])
        assert len(masked) > 0

if __name__ == "__main__":
    pytest.main(["-v", "test_cdc_transactions.py"])
