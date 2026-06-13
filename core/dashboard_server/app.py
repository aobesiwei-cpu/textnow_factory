from database.db_utils import engine, Base
from database.db_models import TbAccount, TbReplyRule, TbAdminUser
from utils.encrypt_util import hash_pwd

def init_tables():
    Base.metadata.create_all(bind=engine)
    print("数据表初始化完成")

def create_super_admin():
    from config.db_config import SessionLocal
    db = SessionLocal()
    exist = db.query(TbAdminUser).filter_by(username="admin").first()
    if not exist:
        admin = TbAdminUser(
            username="admin",
            password_hash=hash_pwd("admin123"),
            is_super=1
        )
        db.add(admin)
        db.commit()
        print("默认管理员账号创建成功：admin / admin123，上线务必修改密码")
    db.close()

if __name__ == "__main__":
    init_tables()
    create_super_admin()