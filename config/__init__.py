import os
from dotenv import load_dotenv

APPLICATION_ROOT_PATH = f"{os.getcwd()}"
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__).replace("config", ".env")))
# load environment variables

