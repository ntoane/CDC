"""
Manage ussd_session state and state transitions
"""
# import cx_Oracle
import logging
from dataclasses import dataclass
from resources.static.response_templates import EXECUTION_SUCCESS, EXECUTION_FAIL
from models.ussd_session_state import USSDSessionState
from resources.utilities.database.oracle import exadata_db


@dataclass
class USSDSession:
    session_uid: str
    msisdn: str = None
    user_input: str = None
    current_state: str = None
    session_start: str = None
    session_last_update: str = None
    terminate_session: bool = False

    def initialize(self):
        query = f"INSERT INTO CDC_USSD_SESSION VALUES({self.session_uid}, 'INIT', 'N.A', 0,'{self.msisdn}', '{self.user_input}', SYSDATE, SYSDATE)"
        print(
            f"\n---\n{USSDSession.initialize.__qualname__} [query]\n{query}"
        )
        try:
            result = self.execute_query(query, "commit")
            print(f"{result}\n---")
            return result
        except Exception as e:
            logging.exception(e, exc_info=True)
            return EXECUTION_FAIL

    def execute(self):
        # check ussd_session exists/status

        # return next state
        pass

    def get_current_state(self):
        query = f"SELECT SESSION_UID, CURRENT_STATE, CURRENT_STATE_ALIAS, CURRENT_STATE_PHASE, MSISDN, USER_INPUT FROM CDC_USSD_SESSION WHERE SESSION_UID='{self.session_uid}'"
        print(
            f"\n---\n{USSDSession.get_current_state.__qualname__} [query]\n{query}"
        )
        try:
            result = self.execute_query(query, "fetch")
        except Exception as e:
            logging.exception(e, exc_info=True)
            return EXECUTION_FAIL
        if result:
            print(f"{result}\n---")
            return {"success": True, "data": {
                "session_uid": result[0],
                "current_state": result[1],
                "current_state_alias": result[2],
                "current_state_phase": result[3],
                "msisdn": result[4],
                "user_input": result[5]}}
        return EXECUTION_FAIL

    def get_next_state(self):
        __next_state = USSDSessionState(session_uid=self.session_uid, user_selection=self.user_input).get_next_state(session_current_state=self.get_current_state())
        return __next_state

    def set_next_state(self, next_state: str, next_state_alias: str, next_state_phase: int = 0):
        query = f"UPDATE CDC_USSD_SESSION SET CURRENT_STATE='{next_state}', CURRENT_STATE_ALIAS='{next_state_alias}', CURRENT_STATE_PHASE='{next_state_phase}' WHERE SESSION_UID='{self.session_uid}'"
        print(
            f"\n---\n{USSDSession.set_next_state.__qualname__} [query]\n{query}"
        )
        try:
            result = self.execute_query(query, "commit")
            print(f"{result}\n---")
            return result
        except Exception as e:
            logging.exception(e, exc_info=True)
            return EXECUTION_FAIL
    
    @staticmethod
    def execute_query(query, operation):
        conn = exadata_db.get_connection_handle()
        cursor = conn.cursor()
        cursor.execute(query)
        if operation == "fetch":
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
        elif operation == "commit":
            if cursor.rowcount:
                cursor.execute("commit")
                cursor.close()
                conn.close()
                return EXECUTION_SUCCESS
            return EXECUTION_FAIL
