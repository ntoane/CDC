import os
import config

# print (os.environ)

from flask import Flask
from resources.utilities.database.oracle import exadata_db

app = Flask(__name__)
exadata_db.init(app=app)


def create_app():
    with app.app_context():
        # TODO: register application blueprints
        # 1. authentication blueprint

        # 2. ussd routes blueprint
        from views.blueprints.ussd import ussd_bp
        app.register_blueprint(blueprint=ussd_bp)

        # 3. health check blueprint
        from views.blueprints.health_check import health_check_bp
        app.register_blueprint(blueprint=health_check_bp)

        return app
