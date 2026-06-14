import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Auto-detect database type: SQLite or MySQL
db_type = os.getenv('DB_TYPE', 'sqlite').lower()  # Default to SQLite

if db_type == 'sqlite':
    # SQLite configuration (lightweight, recommended for Render free tier)
    os.makedirs('./data', exist_ok=True)
    db_path = os.getenv('SQLITE_PATH', './data/textnow_factory.db')
    db_path = os.path.abspath(db_path)
    DB_URI = f'sqlite:///{db_path}'
    print(f"[DB Config] Using SQLite: {db_path}")
    
    engine = create_engine(
        DB_URI,
        connect_args={'timeout': 15, 'check_same_thread': False},
        echo=False
    )
else:
    # MySQL configuration
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '3306')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_name = os.getenv('DB_NAME', 'textnow_us')
    
    if not all([db_host, db_user, db_pass]):
        raise ValueError(
            "MySQL connection requires necessary configuration. "
            "Please check the following environment variables: "
            "DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME"
        )
    
    DB_URI = (
        f"mysql+pymysql://{db_user}:{db_pass}"
        f"@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    )
    print(f"[DB Config] Using MySQL: {db_host}:{db_port}/{db_name}")
    
    engine = create_engine(
        DB_URI,
        pool_size=10,
        max_overflow=20,
        pool_recycle=300,
        pool_pre_ping=True,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 补充：获取数据库会话的依赖函数（适配 Flask/API）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()