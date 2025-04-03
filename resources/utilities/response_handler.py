import uuid
from resources.static.response_templates import RESPONSE_MESSAGE_TEMPLATE


# response handler
class XMLResponseBuilder:
    def __init__(self, session_id: str, message: str, response_type: int):
        super().__init__()

        # generate transaction premium reference
        self.__premium_reference = uuid.uuid4()
        self.__session_id = session_id
        self.__message = message
        self.__response_type = str(response_type)

    def __generate_response_xml(self):
        __response_message = RESPONSE_MESSAGE_TEMPLATE.replace("{SESSION_ID}", self.__session_id) \
            .replace("{RESPONSE_TYPE}", self.__response_type).replace("{MESSAGE}", self.__message) \
            .replace("{PREMIUM_REFERENCE}", str(self.__premium_reference))

        return __response_message

    def get_response_body(self):
        return self.__generate_response_xml()