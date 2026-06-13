from flask import Blueprint, request
from utils.jwt_util import generate_token
from utils.encrypt_util import check_pwd
from database.db_utils import get_db
from database.db_models import TbAdminUser
from core.dashboard_server.utils.api_response import resp_ok, resp_fail

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/login")
def login():
    data = request.get_json()
    username = data.get("username")
    pwd = data.get("password")
    if not username or not pwd:
        return resp_fail(400, "账号密码不能为空")

    db = next(get_db())
    admin = db.query(TbAdminUser).filter_by(username=username).first()
    db.close()
    if not admin or not check_pwd(pwd, admin.password_hash):
        return resp_fail(401, "用户名或密码错误")

    token = generate_token(admin.id, admin.username)
    return resp_ok(data={"token": token})