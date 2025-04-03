from bs4 import BeautifulSoup
import os
import requests
import logging
from resources.static.response_templates import INPUT_INCOMPLETE, EXECUTION_FAIL
from resources.static.vxview_integration.system_api_templates import GET_SUBSCRIBER_INFO, GET_TARIFF_TYPE


class SystemAPIIntegrationController:
    def __init__(self, msisdn: str):
        super().__init__()
        self.__msisdn = msisdn if msisdn else None
        self.__vxview_session_uid = os.environ[
            "VXVIEW_SYSTEM_API_SESSION_ID"] if "VXVIEW_SYSTEM_API_SESSION_ID" in os.environ.keys() else None
        self.__headers = {
            "Content-Type": "text/xml"
        }

    def __call_api(self, payload: str):
        __response = requests.post(url=os.environ["VXVIEW_SYSTEM_API_ENDPOINT"], headers=self.__headers, data=payload,
                                   verify=False)

        if __response.status_code == 200:
            __response = __response.text.replace("&lt;", "<").replace("&gt;", ">").strip()
            return BeautifulSoup(__response, features='xml')
        return None

    def get_subscriber_info(self):
        if not self.__vxview_session_uid or not self.__msisdn:
            return INPUT_INCOMPLETE

        __payload = GET_SUBSCRIBER_INFO.replace("{SESSIONID}", self.__vxview_session_uid).replace("{MSISDN}",
                                                                                                  self.__msisdn)
        print(
            f"\n---\n{SystemAPIIntegrationController.get_subscriber_info.__qualname__} [__payload]\n{__payload}\n---"
        )

        __profile = self.__call_api(payload=__payload)
        __code = __profile.find("Code").text

        print(
            f"\n---\n{SystemAPIIntegrationController.get_subscriber_info.__qualname__} [__profile_code] -- {__code}\n---"
        )

        if __profile and __code == "SystemAPI-Success":
            return {
                "success": True,
                "data": {"subscriber_uid": __profile.find("SubscriberUID").get_text(),
                         "imsi": __profile.find("IMSI").get_text(),
                         "account_number": __profile.find("AccountNumber").get_text(),
                         "account_type": __profile.find("AccountType").get_text(),
                         "name": __profile.find("SubscriberName").get_text(),
                         "surname": __profile.find("Surname").get_text(),
                         "id_number": __profile.find("IDNumber").get_text(),
                         "iccid": __profile.find("ICCID").get_text()}
            }
        logging.error("Subscriber profile not returned from VXView")
        return EXECUTION_FAIL

    def get_tariff_type(self):
        if not self.__vxview_session_uid or not self.__msisdn:
            return INPUT_INCOMPLETE

        __payload = GET_TARIFF_TYPE.replace("{SESSIONID}", self.__vxview_session_uid).replace("{MSISDN}",
                                                                                              self.__msisdn)
        print(
            f"\n---\n{SystemAPIIntegrationController.get_tariff_type.__qualname__} [__payload]\n{__payload}\n---"
        )

        __tariff = self.__call_api(payload=__payload)
        __code = __tariff.find("Code").text
        
        print(
            f"\n---\n{SystemAPIIntegrationController.get_tariff_type.__qualname__} [__tariff_code] -- {__code}\n---"
        )

        if __tariff and __code == "SystemAPI-Success":
            return {
                "success": True,
                "data": {"rateplan_uid": __tariff.find("RatePlanUID").get_text(),
                         "rateplan_name": __tariff.find("RatePlanName").get_text(),
                         "platform_id": __tariff.find("PlatformID").get_text(),
                         "package_type": __tariff.find("PackageType").get_text(),
                         "tariff_type": __tariff.find("TariffType").get_text(),
                         "account_type_name": __tariff.find("AccountTypeName").get_text(),
                         "subscriber_uid": __tariff.find("SubscriberUid").get_text(),
                         "voice_oob": __tariff.find("VoiceOOB").get_text(),
                         "data_oob": __tariff.find("DataOOB").get_text(),
                         "sms_oob": __tariff.find("SmsOOB").get_text(),
                         "activation_date": __tariff.find("ActivationDate").get_text(),
                         }
            }
        logging.error("Subscriber tariff data not returned from VxView")
        return EXECUTION_FAIL
