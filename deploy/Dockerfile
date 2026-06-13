# TextNow 客服系统 - Dockerfile
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装 Python 包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8899

# 等待数据库就绪的脚本
COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

# 启动命令：先等待数据库就绪，再初始化数据库（仅建表），最后启动应用
CMD ["sh", "-c", "python wait_for_db.py --host db --port 3306 --user root --password rootpassword && python init_db.py && python tn_web_dashboard.py"]
