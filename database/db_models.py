from sqlalchemy import Column, Integer, String, DateTime, func
from database.db_utils import Base

class TbAccount(Base):
    __tablename__ = "tb_account"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, comment="账号")
    password = Column(String(255), comment="密码哈希")
    phone = Column(String(32), index=True, comment="手机号")
    status = Column(Integer, index=True, default=0, comment="0正常 1封禁 2待重试 3配额耗尽")
    retry_count = Column(Integer, default=0, comment="注册重试次数")
    proxy_group = Column(String(64), index=True)
    register_time = Column(DateTime, default=func.now())
    ban_reason = Column(String(512), default="")
    is_deleted = Column(Integer, default=0, index=True, comment="逻辑删除")

class TbReplyRule(Base):
    __tablename__ = "tb_reply_rule"
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(200), index=True)
    reply_content = Column(String(1000))
    enable = Column(Integer, default=1)
    create_time = Column(DateTime, default=func.now())

class TbAdminUser(Base):
    __tablename__ = "tb_admin_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(255))
    is_super = Column(Integer, default=0)
    create_time = Column(DateTime, default=func.now())