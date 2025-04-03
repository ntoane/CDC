from flask import Blueprint, make_response, json
from resources.static.response_templates import SYSTEM_HEALTH_CHECK_SUCCESS, SYSTEM_HEALTH_CHECK_FAIL
import os

health_check_bp = Blueprint(name="health-check", import_name=__name__, url_prefix="/app")

@health_check_bp.route("/health", methods=["GET"], strict_slashes=False)
def health():
    return make_response(json.dumps(SYSTEM_HEALTH_CHECK_SUCCESS), 200)
