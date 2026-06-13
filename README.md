# TextNow 账号自动化运营工厂
商业级高并发TextNow账号注册+客服对话+Web管理后台一体化项目
支持日注册十万级账号、动态住宅代理、iOS设备指纹模拟、可视化后台管理

## 目录结构
textnow_factory/
├── config/         环境、数据库、全局参数配置
├── core/           三大核心业务源码（注册/客服/后台服务）
├── database/       SQL建表语句、数据库初始化、迁移工具
├── utils/          日志、请求、指纹、通用工具封装
├── deploy/         容器部署全套配置
├── data/           运行日志、临时数据（不会提交Git）
├── archive/        历史旧脚本归档存放，不参与运行

## 快速部署
1. 安装依赖
pip install -r requirements.txt

2. 配置环境变量
cp config/.env.example .env
编辑.env填入数据库、代理、密钥信息

3. 初始化数据库
make init-db

4. 启动服务
make start-dashboard
make start-register
make start-cs

## 容器部署
make deploy-up
make deploy-down

## 安全说明
.env、数据库密钥已加入.gitignore，禁止上传代码仓库；后台增加鉴权限制访问。
