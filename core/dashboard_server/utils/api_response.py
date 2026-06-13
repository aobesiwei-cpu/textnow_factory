from flask import jsonify, request
from functools import wraps
from utils.jwt_util import verify_token

def resp_ok(data=None, msg="success"):
    return jsonify({"code": 200, "msg": msg, "data": data})

def resp_fail(code=400, msg="fail", data=None):
    return jsonify({"code": code, "msg": msg, "data": data})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return resp_fail(401, "未授权，请登录")
        payload = verify_token(token)
        if not payload:
            return resp_fail(401, "Token无效或过期")
        return f(payload, *args, **kwargs)
    return decorated