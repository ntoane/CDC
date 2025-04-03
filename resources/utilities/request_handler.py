from bs4 import BeautifulSoup


# request handler
class XMLRequestParser:
    def __init__(self, xml_post_data: bytes = None):
        super().__init__()

        if xml_post_data:
            self.__request_body = str(xml_post_data.decode("UTF-8"))
            self.__request_data = self.__request_data_to_json()

    def __request_data_to_json(self):
        """
        transform request xml to json format
        :return: dict
        """
        request_data = BeautifulSoup(self.__request_body, features="xml")
        if not request_data:
            return None

        return {
            "msisdn": request_data.find("msisdn").text,
            "session_id": request_data.find("sessionid").text,
            "request_phase": request_data.find("phase").text,
            "request_type": request_data.find("request")["type"],
            "request_input": request_data.find("request").text
        }

    def __generate_response_body(self, **kwargs):
        pass

    def get_request_data(self):
        return self.__request_data
