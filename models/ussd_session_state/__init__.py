"""
Based on current ussd_session_state uid and user selection/input; you transition to the next state
"""
# import cx_Oracle
import logging
from dataclasses import dataclass
from resources.static.response_templates import EXECUTION_FAIL
from resources.utilities.database.oracle import exadata_db


@dataclass
class USSDSessionState:
    session_uid: str
    user_selection: str
    current_state: str = None
    menu_uid: int = None
    next_state: str = None
    next_state_message: str = None
    next_state_user_input_required: str = None
    next_state_alias: str = None
    next_state_phase: str = None

    def get_next_state(self, session_current_state: object):
        __current_state = session_current_state
        print(f"\n---\n Current State:: {USSDSessionState.get_next_state.__qualname__}\n{__current_state}\n---")

        if not __current_state["success"]:
            return EXECUTION_FAIL

        if __current_state["data"]["current_state"] == 'INIT':
            query = f"SELECT NEXT_STATE, NEXT_STATE_MESSAGE, NEXT_STATE_INPUT_REQUIRED, NEXT_STATE_ALIAS, NEXT_STATE_PHASE FROM CDC_USSD_SESSION_STATE \
            WHERE CURRENT_STATE='{__current_state['data']['current_state']}'"
            print(
                f"\n---\n{USSDSessionState.get_next_state.__qualname__} [query]\n{query}"
            )
        
        # menu with no constant state and phase transitions
        else:
            query = f"SELECT NEXT_STATE, NEXT_STATE_MESSAGE, NEXT_STATE_INPUT_REQUIRED, NEXT_STATE_ALIAS, NEXT_STATE_PHASE FROM CDC_USSD_SESSION_STATE \
            WHERE CURRENT_STATE='{__current_state['data']['current_state']}' AND NEXT_STATE_USER_SELECTION='{self.user_selection}'"
            print(
                f"\n---\n{USSDSessionState.get_next_state.__qualname__} [query]\n{query}"
            )
            
        try:
            result = self.execute_query(query)
        except Exception as e:
            logging.exception(e, exc_info=True)
            return EXECUTION_FAIL
        if result:
            print(f"{result}\n---")
            return {
                "success": True,
                "data": {
                    "session_uid": __current_state["data"]["session_uid"],
                    "next_state": result[0],
                    "next_state_message": result[1],
                    "next_state_input_required": result[2],
                    "next_state_alias": result[3],
                    "next_state_phase": result[4]
                }
            }
        return EXECUTION_FAIL

    def get_custom_state(self, current_state):
            query = f"SELECT NEXT_STATE, NEXT_STATE_MESSAGE, NEXT_STATE_INPUT_REQUIRED, NEXT_STATE_ALIAS, NEXT_STATE_PHASE FROM CDC_USSD_SESSION_STATE \
                WHERE CURRENT_STATE='{current_state}'"
            print(
                f"\n---\n{USSDSessionState.get_custom_state.__qualname__} [query]\n{query}"
            )
            try:
                result = self.execute_query(query)
            except Exception as e:
                logging.exception(e, exc_info=True)
                return EXECUTION_FAIL
            if result:
                print(f"{result}\n---")
                return {
                    "success": True,
                    "data": {
                        "next_state": result[0],
                        "next_state_message": result[1],
                        "next_state_input_required": result[2],
                        "next_state_alias": result[3],
                        "next_state_phase": result[4]
                    }
                }
            return EXECUTION_FAIL
    
    @staticmethod
    def execute_query(query):
        conn = exadata_db.get_connection_handle()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result