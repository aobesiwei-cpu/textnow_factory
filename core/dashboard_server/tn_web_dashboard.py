"""
TextNow Factory - Web Dashboard (Flask)
Render 部署入口
"""
import os
from flask import Flask, render_template, request, redirect, url_for
from config.db_config import engine, Base, SessionLocal
from database.db_models import TbAccount, TbReplyRule, TbAdminUser
from utils.encrypt_util import hash_pwd

# 创建 Flask 应用
app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)
app.secret_key = os.getenv("TN_SECRET_KEY", "textnow-cs-secret-key-2026")

# 注册路由蓝图
from routes.auth_route import auth_bp
from routes.account_route import account_bp
from routes.rule_route import rule_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(account_bp, url_prefix='/api/accounts')
app.register_blueprint(rule_bp, url_prefix='/api/rules')


@app.route('/')
def index():
    """首页 - 重定向到登录或仪表盘"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth_bp.login'))


@app.route('/dashboard')
def dashboard():
    """仪表盘主页"""
    return render_template('dashboard.html')


# 初始化数据库
with app.app_context():
    Base.metadata.create_all(bind=engine)
    # 创建默认管理员
    db = SessionLocal()
    try:
        exist = db.query(TbAdminUser).filter_by(username="admin").first()
        if not exist:
            admin = TbAdminUser(
                username="admin",
                password_hash=hash_pwd("admin123"),
                is_super=1
            )
            db.add(admin)
            db.commit()
            print("✅ 默认管理员已创建: admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
