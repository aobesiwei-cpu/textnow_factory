from flask import Blueprint, request
from sqlalchemy import or_
from core.dashboard_server.utils.api_response import resp_ok, token_required
from database.db_utils import get_db
from database.db_models import TbAccount

account_bp = Blueprint("account", __name__)

@account_bp.get("/list")
@token_required
def get_account_list(payload):
    db = next(get_db())
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 10))
    kw = request.args.get("kw", "").strip()
    status = request.args.get("status", "")

    q = db.query(TbAccount).filter(TbAccount.is_deleted == 0)
    if status:
        q = q.filter(TbAccount.status == int(status))
    if kw:
        q = q.filter(or_(
            TbAccount.username.like(f"%{kw}%"),
            TbAccount.phone.like(f"%{kw}%")
        ))

    total = q.count()
    pages = (total + size - 1) // size
    data_list = q.limit(size).offset((page-1)*size).all()

    res_list = []
    for row in data_list:
        res_list.append({
            "id": row.id,
            "username": row.username,
            "phone": row.phone,
            "status": row.status,
            "proxy_group": row.proxy_group,
            "retry_count": row.retry_count,
            "register_time": row.register_time.strftime("%Y-%m-%d %H:%M:%S") if row.register_time else ""
        })
    db.close()
    return resp_ok(data={
        "list": res_list,
        "total": total,
        "pages": pages,
        "page": page,
        "size": size
    })