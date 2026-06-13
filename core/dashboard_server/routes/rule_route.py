from flask import Blueprint
from core.dashboard_server.utils.api_response import resp_ok, token_required

rule_bp = Blueprint("rule", __name__)

@rule_bp.get("/list")
@token_required
def rule_list(payload):
    return resp_ok(data={"msg":"回复规则接口就绪"})