DROP SEQUENCE CDC_USSD_SESSION_STATE_SEQ;
DROP TABLE CDC_USSD_SESSION_STATE;

DROP SEQUENCE CDC_USSD_SESSION_SEQ;
DROP TABLE CDC_USSD_SESSION;

CREATE SEQUENCE CDC_USSD_SESSION_STATE_SEQ INCREMENT BY 1 START WITH 1 MINVALUE 1 NOMAXVALUE NOCACHE;
CREATE TABLE CDC_USSD_SESSION_STATE (
	SESSION_STATE_UID INT UNIQUE NOT NULL, -- SEQ UNIQUE ID
	CURRENT_STATE VARCHAR2(254), -- CURRENT MENU PRESENTED TO THE CUSTOMER
	NEXT_STATE_USER_SELECTION INT NOT NULL, -- ID FOR MENU / SUB MENU RELATIVE TO CURRENT STATE
	NEXT_STATE VARCHAR2(254), -- NEXT MENU STATE
	NEXT_STATE_MESSAGE VARCHAR2(512), -- AFTER WE PRESENT THE CUSTOMER THIS (NEXT STATE)
	NEXT_STATE_INPUT_REQUIRED CHAR(1) NOT NULL, -- DO WE NEED INPUT OR NOT
	NEXT_STATE_ALIAS VARCHAR2(254) DEFAULT 'N.A', -- A STATE CAN REQUIRE MULTIPLE INPUT, REQUEST INPUT IN PHASES (PHASES HAVE ALPHANUMERIC NAMES)
	NEXT_STATE_PHASE INT DEFAULT 0 -- STATE PHASES SHOULD BE IN ASCENDING ORDER
);

-- USSD SESSION STATE
INSERT INTO CDC_USSD_SESSION_STATE VALUES (CDC_USSD_SESSION_STATE_SEQ.NEXTVAL, 'INIT', 5, 'TRANSACTIONS', 'Transaction History' ||CHR(10)|| '1. Airtime Transfer History' ||CHR(10)|| '2. Bundle Purchases History' ||CHR(10)|| '3. Call Records', 'Y', 'N.A', 0);
INSERT INTO CDC_USSD_SESSION_STATE VALUES (CDC_USSD_SESSION_STATE_SEQ.NEXTVAL, 'TRANSACTIONS', 1, 'AIRTIME_TRANSACTIONS', 'Your airtime transfer history will be sent to you shortly via SMS.', 'N', 'N.A', 0);
INSERT INTO CDC_USSD_SESSION_STATE VALUES (CDC_USSD_SESSION_STATE_SEQ.NEXTVAL, 'TRANSACTIONS', 2, 'BUNDLE_TRANSACTIONS', 'Your bundle purchase history will be sent to you shortly via SMS.', 'N', 'N.A', 0);
INSERT INTO CDC_USSD_SESSION_STATE VALUES (CDC_USSD_SESSION_STATE_SEQ.NEXTVAL, 'TRANSACTIONS', 3, 'CALL_TRANSACTIONS', 'Your call data records will be sent to you shortly via SMS.', 'N', 'N.A', 0);


CREATE SEQUENCE CDC_USSD_SESSION_SEQ INCREMENT BY 1 START WITH 1 MINVALUE 1 NOMAXVALUE NOCACHE;
CREATE TABLE CDC_USSD_SESSION (
	SESSION_UID VARCHAR2(254) UNIQUE NOT NULL,
	CURRENT_STATE VARCHAR2(254) NOT NULL,
	CURRENT_STATE_ALIAS VARCHAR2(254) NOT NULL,
    CURRENT_STATE_PHASE INT NOT NULL,
	MSISDN VARCHAR2(11),
	USER_INPUT VARCHAR2(254) NOT NULL,
	CREATED_ON TIMESTAMP DEFAULT SYSDATE,
	MODIFIED_ON TIMESTAMP DEFAULT SYSDATE
);

CREATE TABLE TRANSACTION_REQUESTS (
    REQUEST_UID VARCHAR2(36) PRIMARY KEY,
    MSISDN VARCHAR2(15) NOT NULL,
    REQUEST_TYPE VARCHAR2(20) NOT NULL,
    RESPONSE_TEXT CLOB,
    CREATED_ON TIMESTAMP DEFAULT SYSTIMESTAMP,
    PROCESSED_ON TIMESTAMP,
    CONSTRAINT CK_REQUEST_TYPE CHECK (REQUEST_TYPE IN ('AIRTIME_TRANSFER', 'BUNDLE_PURCHASE', 'CALL_RECORDS'))
);

-- Create index on MSISDN for faster lookups
CREATE INDEX IDX_TR_MSISDN ON TRANSACTION_REQUESTS(MSISDN);

-- Create index on created date for reporting
CREATE INDEX IDX_TR_CREATED_ON ON TRANSACTION_REQUESTS(CREATED_ON);

COMMIT;

