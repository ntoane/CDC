from flask import json, make_response, request, Blueprint

from controllers.ussd_session import USSDSessionController
from resources.utilities.response_handler import XMLResponseBuilder
from resources.static.response_templates import APPLICATION_ERRORED
from resources.static.response_templates import REQUEST_INPUT_INCOMPLETE
from resources.utilities.request_handler import XMLRequestParser

ussd_bp = Blueprint(name="ussd", import_name=__name__, url_prefix="/")

@ussd_bp.route("/", methods=["POST"], strict_slashes=False)
def ussd():
    if request.data:
        try:
            __session_handler = USSDSessionController(request_data=request.data)
            __response = __session_handler.process_request()

            if __response:
                return make_response(__response)
            
            # Processing failed
            __request_data = XMLRequestParser(xml_post_data=request.data).get_request_data()
            __response_xml = XMLResponseBuilder(session_id=__request_data["session_id"],
                                                response_type=3,
                                                message=APPLICATION_ERRORED["data"]["message"])

            return make_response(__response_xml.get_response_body())

        except Exception as e:
            return make_response("Internal Server Error", 500)

    # Required inputs not provided
    __response_xml = XMLResponseBuilder(session_id="000",
                                        response_type=3,
                                        message=REQUEST_INPUT_INCOMPLETE["data"]["message"])
    
    return make_response(__response_xml.get_response_body())