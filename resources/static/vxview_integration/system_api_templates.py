GET_SUBSCRIBER_INFO = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.api.system.vasx.com/">
               <soapenv:Header/>
               <soapenv:Body>
                  <ser:getSubscriberInfo>
                     <!--Optional:-->
                     <SessionID>{SESSIONID}</SessionID>
                     <!--Optional:-->
                     <ActionDate></ActionDate>
                     <!--Optional:-->
                     <VirtualNetwork>1</VirtualNetwork>
                     <!--Optional:-->
                     <MSISDN>{MSISDN}</MSISDN>
                  </ser:getSubscriberInfo>
               </soapenv:Body>
            </soapenv:Envelope>"""

GET_TARIFF_TYPE = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ser=\"http://service.api.system.vasx.com/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <ser:getTariffType>
                     <!--Optional:-->
                     <SessionID>{SESSIONID}</SessionID>
                     <!--Optional:-->
                     <MSISDN>{MSISDN}</MSISDN>
                  </ser:getTariffType>
               </soapenv:Body>
            </soapenv:Envelope>"""

CHANGE_FREE_TARIFF = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ser=\"http://service.api.system.vasx.com/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <ser:changeFreeTarrif>
                     <!--Optional:-->
                     <SessionID>{SESSIONID}</SessionID>
                     <!--Optional:-->
                     <ProvID>{PROVIDERID}</ProvID>
                     <!--Optional:-->
                     <MSISDN>{MSISDN}</MSISDN>
                  </ser:changeFreeTarrif>
               </soapenv:Body>
            </soapenv:Envelope>"""

POSTPAID_BALANCE_ENQUIRY = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ser=\"http://service.api.system.vasx.com/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <ser:postpaidBalanceEnquiry>
                     <!--Optional:-->
                     <SessionID>{SESSIONID}</SessionID>
                     <!--Optional:-->
                     <VirtualNetwork>1</VirtualNetwork>
                     <!--Optional:-->
                     <MSISDN>{MSISDN}</MSISDN>
                     <!--Optional:-->
                     <ActionDate></ActionDate>
                  </ser:postpaidBalanceEnquiry>
               </soapenv:Body>
            </soapenv:Envelope>"""

OPTIN = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ser=\"http://service.api.system.vasx.com/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <ser:OptIn>
                     <!--Optional:-->
                     <SessionID>{SESSIONID}</SessionID>
                     <!--Optional:-->
                     <MSISDN>{MSISDN}</MSISDN>
                     <!--Optional:-->
                     <StockCode>{STOCKCODE}</StockCode>
                     <!--Optional:-->
                     <ProductCode>{PRODUCTCODE}</ProductCode>
                     <!--Optional:-->
                     <Action>{ACTION}</Action>
                  </ser:OptIn>
               </soapenv:Body>
            </soapenv:Envelope>"""

UPDATE_SUBSCRIBER_SERVICE = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ser=\"http://service.api.system.vasx.com/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <ser:updateSubscriberService>
                     <!--Optional:-->
                     <SessionID>{SESSIONID}</SessionID>
                     <!--Optional:-->
                     <VirtualNetwork>1</VirtualNetwork>
                     <!--Optional:-->
                     <SubscriberUID>{SUBUID}</SubscriberUID>
                     <!--Optional:-->
                     <ServiceUID>{SRVUID}</ServiceUID>
                     <!--Optional:-->
                     <ReasonCode></ReasonCode>
                     <!--Optional:-->
                     <Action>{ACTION}</Action>
                     <!--Optional:-->
                     <ActionDate></ActionDate>
                  </ser:updateSubscriberService>
               </soapenv:Body>
            </soapenv:Envelope>"""

PURCHASE_PRODUCT = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ser=\"http://service.api.system.vasx.com/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <ser:purchaseProduct>
                     <!--Optional:-->
                     <SessionID>{SESSIONID}</SessionID>
                     <!--Optional:-->
                     <MSISDN>{MSISDN}</MSISDN>
                     <!--Optional:-->
                     <SubscriberUID></SubscriberUID>
                     <!--Optional:-->
                     <AccountNumber></AccountNumber>
                     <!--Optional:-->
                     <StockCode>{STOCKCODE}</StockCode>
                     <!--Optional:-->
                     <ProductCode>{PRODUCTCODE}</ProductCode>
                     <!--Optional:-->
                     <Description></Description>
                     <!--Optional:-->
                     <VirtualNetwork>1</VirtualNetwork>
                  </ser:purchaseProduct>
               </soapenv:Body>
            </soapenv:Envelope>"""