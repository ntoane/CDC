import json
import os
import logging
from resources.utilities.database.oracle import exadata_db
# from resources.utilities.sms_service import sms_service
from resources.static.response_templates import EXECUTION_FAIL
import uuid
from resources.utilities.sms_service import sms_logger
from resources.utilities.sms_sender import SMS


class CDCTransactions:
    """
    A class for managing Customer Data Connect transaction information.

    This class provides functionality to read transactions for airtime transfers, bunddle purchases and call data records.

    Attributes:
    cdc_transactions_file (str): Path to the JSON file containing transaction data.
    """

    def get_airtime_transfers(self, msisdn: str):
        try:
            # Record the request
            request_id = str(uuid.uuid4())
            insert_query = f"""
                INSERT INTO TRANSACTION_REQUESTS 
                (REQUEST_UID, MSISDN, REQUEST_TYPE, CREATED_ON) 
                VALUES 
                ('{request_id}', '{msisdn}', 'AIRTIME_TRANSFER', SYSTIMESTAMP)
            """
            self.execute_query(insert_query, fetch_data=False)
            
            # Query to get the last 5 airtime transfers
            query = f"""
                SELECT *
                FROM (
                    SELECT * 
                    FROM AIRTIME_TRANSFER 
                    WHERE OC_SERVED_MSISDN_NORM = '{msisdn}'
                    ORDER BY OC_RECORDTIMESTAMP DESC
                )
                WHERE ROWNUM <= 5
            """
            
            # Execute query and get results directly
            airtime_transfers = self.execute_query(query, fetch_data=True)
            
            if not airtime_transfers:
                return []

            # Format results for SMS
            sms_items = []
            for i, item in enumerate(airtime_transfers):
                timestamp = item["OC_RECORDTIMESTAMP"].strftime("%d/%m/%Y %H:%M")
                transfered_to = self.mask_phone_number(item["OC_OTHERPARTY_NORM"])
                amount = f"M{item['OC_ACCOUNT_CHARGE']:.2f}"
                message = f"{i+1}) {timestamp} {transfered_to} {amount}"
                sms_items.append({"message": message})

            # Update transaction record with response
            if sms_items:
                sms_message = "\n".join([item["message"] for item in sms_items])
                update_query = f"""
                    UPDATE TRANSACTION_REQUESTS
                    SET RESPONSE_TEXT = '{sms_message}',
                        PROCESSED_ON = SYSTIMESTAMP
                    WHERE REQUEST_UID = '{request_id}'
                """
                self.execute_query(update_query, fetch_data=False)
                
            return sms_items
        except Exception as e:
            logging.exception(e, exc_info=True)
            print(EXECUTION_FAIL)
            return []
    
    def get_bundle_purchases(self, msisdn: str):
        try:
            request_id = str(uuid.uuid4())
            insert_query = f"""
                INSERT INTO TRANSACTION_REQUESTS 
                (REQUEST_UID, MSISDN, REQUEST_TYPE, CREATED_ON) 
                VALUES 
                ('{request_id}', '{msisdn}', 'BUNDLE_PURCHASE', SYSTIMESTAMP)
            """
            self.execute_query(insert_query, fetch_data=False)
        
            # Query to get the last 5 bundle purchases for the given MSISDN
            query = f"""
                SELECT *
                FROM (
                    SELECT * 
                    FROM BUNDLE_PURCHASE 
                    WHERE OC_SERVED_MSISDN_NORM = '{msisdn}'
                    ORDER BY OC_RECORDTIMESTAMP DESC
                )
                WHERE ROWNUM <= 5
            """

            bundle_purchase = self.execute_query(query, fetch_data=True)

            if not bundle_purchase:
                return []

            sms_items = []
            for i, item in enumerate(bundle_purchase):
                timestamp = item["OC_RECORDTIMESTAMP"].strftime("%d/%m/%Y %H:%M")
                other_party = self.mask_phone_number(item["OC_OTHERPARTY_NORM"])
                event = item["EVENT"]
                amount = f"M{item['OC_ACCOUNT_CHARGE']:.2f}"
                # Format message differently based on whether other_party exists
                if other_party and other_party.strip():
                    # Mask the phone number only if it exists
                    masked_party = self.mask_phone_number(other_party)
                    message = f"{i+1}) {masked_party}: {timestamp} {event} {amount}"
                else:
                    message = f"{i+1}) {timestamp} {event} {amount}"
                sms_items.append({"message": message})

            # If successful, update the record with response
            if sms_items:
                sms_message = "\n".join([item["message"] for item in sms_items])
                update_query = f"""
                    UPDATE TRANSACTION_REQUESTS
                    SET RESPONSE_TEXT = '{sms_message}',
                        PROCESSED_ON = SYSTIMESTAMP
                    WHERE REQUEST_UID = '{request_id}'
                """
                self.execute_query(update_query, fetch_data=False)
        
            return sms_items
        except Exception as e:
            logging.exception(e, exc_info=True)
            print(EXECUTION_FAIL)
            return []

    def get_call_records(self, msisdn: str):
        try:
            request_id = str(uuid.uuid4())
            insert_query = f"""
                INSERT INTO TRANSACTION_REQUESTS 
                (REQUEST_UID, MSISDN, REQUEST_TYPE, CREATED_ON) 
                VALUES 
                ('{request_id}', '{msisdn}', 'CALL_RECORDS', SYSTIMESTAMP)
            """
            self.execute_query(insert_query, fetch_data=False)
            
            # Query to get the last 5 call records for the given MSISDN
            query = f"""
                SELECT *
                FROM (
                    SELECT * 
                    FROM CALL_RECORDS 
                    WHERE OC_SERVED_MSISDN_NORM = '{msisdn}'
                    ORDER BY OC_RECORDTIMESTAMP DESC
                )
                WHERE ROWNUM <= 5
            """
            
            call_records = self.execute_query(query, fetch_data=True)

            if not call_records:
                return []

            sms_items = []
            for i, item in enumerate(call_records):
                timestamp = item["OC_RECORDTIMESTAMP"].strftime("%d/%m/%Y %H:%M")
                other_party = self.mask_phone_number(item["OC_OTHERPARTY_NORM"])
                call_duration = self.format_time_duration(item["OC_TOTAL_USED_DURATION"])
                account_balance_after = self.format_time_duration(item['OC_ACCOUNT_BALANCE_AFTER'])
                message = f"{i+1}) {other_party}: {call_duration}, Balance: {account_balance_after}, Date: {timestamp}"
                sms_items.append({"message": message})

                # If successful, update the record with response
            if sms_items:
                sms_message = "\n".join([item["message"] for item in sms_items])
                update_query = f"""
                    UPDATE TRANSACTION_REQUESTS
                    SET RESPONSE_TEXT = '{sms_message}',
                        PROCESSED_ON = SYSTIMESTAMP
                    WHERE REQUEST_UID = '{request_id}'
                """
                self.execute_query(update_query, fetch_data=False)
                
            return sms_items
        except Exception as e:
            logging.exception(e, exc_info=True)
            print(EXECUTION_FAIL)
            return []

    def send_sms(self, msisdn: str, title: str, sms_items: list):
        if not sms_items:
            sms_logger.warning("You have no recent transactions for this request")
            return {
                "success": False,
                "message": "You have no recent transactions for this request"
            }

        try:
            # Join all messages with period breaks and append the title
            items_text = ". " . join([item["message"] for item in sms_items])
            sms_message = f"{title}\n{items_text}"
            
            if not msisdn or msisdn.strip() == "":
                sms_logger.error("Empty or invalid MSISDN provided")
                return {
                    "success": False,
                    "message": "Empty or invalid MSISDN provided"
                }   
            # Send the SMS
            result = SMS.send_sms(msisdn,sms_message)
            
            # Log the result
            if isinstance(result, dict) and result == {'success': True}:
                sms_logger.info(f"Successfully sent SMS to {msisdn}")
                return{
                    "success": True,
                    "message": "Successfully sent SMS to " +  msisdn
                }
            else:
                sms_logger.error(f"Failed to send SMS: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "message": "An error occured when processing your request"
                }   
                
        except Exception as e:
            sms_logger.error(f"Model: Error in send_sms: {str(e)}")
            return {
                "success": False,
                "message": "An error occured when processing your request"
            }   

    @staticmethod
    def mask_phone_number(phone_number):
        if not phone_number:
            return ""
        if len(phone_number) < 8:
            return phone_number  # Return as-is if too short or empty
            
        visible_prefix = phone_number[:5]  # First 5 digits
        visible_suffix = phone_number[-1:]  # Last digit
        masked_length = len(phone_number) - len(visible_prefix) - len(visible_suffix) # Length of the middle part to mask
        masked_part = '*' * masked_length
        
        return f"{visible_prefix}{masked_part}{visible_suffix}"

    @staticmethod
    def format_time_duration(duration_in_minutes):
        """
        Format a decimal duration (in minutes) to a human-readable format 
        like "7min 58sec"
        
        Args:
            duration_in_minutes (float): Duration in minutes
            
        Returns:
            str: Formatted duration string
        """
        # Convert to seconds for easier calculation
        total_seconds = int(duration_in_minutes * 60)
        
        # Calculate minutes and remaining seconds
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # Format the output
        if minutes > 0:
            return f"{minutes}min {seconds}sec"
        else:
            return f"{seconds}sec"
    
    @staticmethod
    def execute_query(query, fetch_data=False):
        """
        Execute a SQL query and handle committing or fetching data as appropriate.
        
        Args:
            query (str): SQL query to execute
            fetch_data (bool): If True, fetch and return data (for SELECT queries)
                            If False, commit the transaction (for INSERT/UPDATE/DELETE)
        
        Returns:
            If fetch_data is True: List of dictionaries with the query results
            If fetch_data is False: True for successful execution
        """
        conn = None
        cursor = None
        try:
            conn = exadata_db.get_connection_handle()
            cursor = conn.cursor()
            cursor.execute(query)
            
            if fetch_data:
                # For SELECT queries - fetch data and return as list of dictionaries
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
                return result
            else:
                # For INSERT/UPDATE/DELETE queries - commit the transaction
                conn.commit()
                return True
                
        except Exception as e:
            # Roll back any changes if there was an error
            if conn:
                conn.rollback()
            logging.error(f"Database error: {str(e)}")
            raise
        finally:
            # Clean up resources
            if cursor:
                cursor.close()
            if conn:
                conn.close()
