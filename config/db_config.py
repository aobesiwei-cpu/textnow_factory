import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# 自动检测数据库类型：SQLite 或 MySQL
db_type = os.getenv('DB_TYPE', 'sqlite').lower()  # 默认使用 SQLite

if db_type == 'sqlite':
    # SQLite 配置（Render 免费部署推荐）
    db_path = os.getenv('SQLITE_PATH', './data/textnow_factory.db')
    DB_URI = f'sqlite:///{db_path}'
else:
    # MySQL 配置
    DB_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    )

# 连接池配置
engine = create_engine(
    DB_URI,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)