import cx_Oracle
import config
import os

# cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\molet013\Repo\instantclient_12_2")

class ExaDataDatabase:
    def __init__(self):
        super().__init__()
        self.conn = None
        self.app = None

        self.db_config = {
            "user": os.environ["EXADATA_DB_USERNAME"],
            "pass": os.environ["EXADATA_DB_PASSWORD"],
            "sid": os.environ["EXADATA_DB_SERVICE_NAME"],
            "port": os.environ["EXADATA_DB_PORT"],
            "host": os.environ["EXADATA_DB_HOSTNAME"]
        }

    def init(self, app: object):
        if app is None:
            raise Exception("App instance not provided")
        self.app = app

    def get_connection_handle(self):
        dsn_tns = cx_Oracle.makedsn(self.db_config["host"], self.db_config["port"], service_name=self.db_config["sid"])
        self.conn = cx_Oracle.connect(user=self.db_config["user"], password=self.db_config["pass"], dsn=dsn_tns, threaded=True)
        return self.conn

exadata_db = ExaDataDatabase()