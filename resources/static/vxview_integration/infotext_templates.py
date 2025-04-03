PURCHASE_DYNAMIC_BUNDLES = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:web=\"http://web.services.infotext.vasx.com.au/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <web:purchaseDynamicBundle>
                     <!--Optional:-->
                     <DynamicBundlesInputBean>
                        <!--Optional:-->
                        <bundlecode>{BUNDLECODE}</bundlecode>
                        <!--Optional:-->
                        <languageCode>en</languageCode>
                        <!--Optional:-->
                        <MSISDN>{MSISDN}</MSISDN>
                        <!--Optional:-->
                        <sessionID></sessionID>
                        <size>{BUNDLESIZE}</size>
                        <vnUID>1</vnUID>
                     </DynamicBundlesInputBean>
                  </web:purchaseDynamicBundle>
               </soapenv:Body>
            </soapenv:Envelope>"""

XCE_API_QUERY_BUNDLE = """
            <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:web=\"http://webservice.xce.vasx.au/\">
               <soapenv:Header/>
               <soapenv:Body>
                  <web:queryBundle>
                     <!--Optional:-->
                     <msisdn>{MSISDN}</msisdn>
                     <!--Optional:-->
                     <transactionId>?</transactionId>
                  </web:queryBundle>
               </soapenv:Body>
            </soapenv:Envelope>"""

