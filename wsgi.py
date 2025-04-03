activate_this = '/var/www/html/python-applications/customer-data-connect/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
import site
sys.path.insert(0, "/var/www/html/python-applications/customer-data-connect/")
site.addsitedir("/var/www/html/python-applications/customer-data-connect/venv/lib64/python3.6/site-packages/")

from views import create_app

application = create_app()