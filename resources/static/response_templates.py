"""
Response message templates
"""
SYSTEM_HEALTH_CHECK_SUCCESS = {"success": True, "code": 0, "data": {"message": "API is up and running!"}}
SYSTEM_HEALTH_CHECK_FAIL = {"success": True, "code": 1, "data": {"message": "API is NOT up and running!"}}

REQUEST_INPUT_INCOMPLETE = {"success": False, "data": {"message": "Missing input in the request!"}}
INPUT_INCOMPLETE = {"success": False, "data": {"message": "Required input missing. Check input."}}
EXECUTION_SUCCESS = {"success": True}
EXECUTION_FAIL = {"success": False, "data": {"message": "Failed to process your request."}}
APPLICATION_ERRORED = {"success": False, "data": {"message": "Request could not be processed at this time. Please try again later."}}
SERVICE_NOT_ALLOWED = {"success": False, "data": {"message": "Service not allowed on this number."}}

# ussd response template
RESPONSE_MESSAGE_TEMPLATE = "<msg><sessionid>{SESSION_ID}</sessionid>\
    <response type='{RESPONSE_TYPE}'>{MESSAGE}</response>\
    <premium reference='{PREMIUM_REFERENCE}'>000</premium></msg>"
