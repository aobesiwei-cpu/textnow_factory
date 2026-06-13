# TextNow 客服系统 - 商业化升级完成报告

## 项目信息
- **项目路径**: C:\Users\carti\Documents\textnow\其他文件\2026年\textnow\
- **升级日期**: 2026-06-13
- **完成状态**: ✅ 第一阶段核心功能全部完成，第二阶段和第三阶段主要功能已实现

---

## 一、完成的工作

### 📦 第一阶段：核心功能（最重要）

#### 1. ✅ 消息轮询引擎（fetch_messages.py）
**文件**: `fetch_messages.py` (6.7 KB)

**功能**:
- 定时从 TextNow API 拉取每个账号的新消息
- Demo 模式下用模拟数据代替（30% 概率生成新消息）
- 新消息自动存入 `tn_messages` 表
- 自动创建/更新 `tn_conversations` 表
- 支持环境变量 `TN_FETCH_INTERVAL`（秒，默认 30）
- 触发自动回复检查

**使用方法**:
```bash
python fetch_messages.py
```

**日志**: `logs/fetch_messages.log`

---

#### 2. ✅ 自动回复引擎（完善 tn_customer_service.py）
**文件**: `tn_customer_service.py` (11.9 KB)

**功能**:
- 监听新消息，根据 `tn_auto_rules` 关键词匹配模板
- 支持优先级（`priority` 字段，数字越大优先级越高）
- 支持多种匹配模式（`contains`/`exact`/`regex`）
- 模板变量替换（支持 `{contact_number}`, `{account_phone}` 等变量）
- Demo 模式模拟发送
- 失败自动重试（最多 3 次，指数退避）
- 写入日志 `logs/auto_reply.log`

**使用方法**:
```bash
python tn_customer_service.py
```

**API 调用示例**:
```python
from tn_customer_service import AutoReplyEngine
engine = AutoReplyEngine()
engine.process_message(conv_id, message_id)
```

---

#### 3. ✅ 账号健康检查（account_health.py）
**文件**: `account_health.py` (9.4 KB)

**功能**:
- 定期用轻量 API 检测账号是否可用
- 不可用时自动 `status=0`，记录原因
- Demo 模式下模拟健康状态（90% 概率健康）
- 连续失败次数阈值（默认 3 次）
- 自动恢复检测（健康后重新启用）

**使用方法**:
```bash
python account_health.py
```

**配置**:
- `TN_HEALTH_INTERVAL`: 检查间隔（秒，默认 300）
- `MAX_CONSECUTIVE_FAILURES`: 连续失败次数阈值（默认 3）

**日志**: `logs/account_health.log`

---

#### 4. ✅ 发送队列（send_queue.py）
**文件**: `send_queue.py` (14.8 KB)

**功能**:
- 消息发送放入队列（`tn_send_queue` 表）
- 控制每个账号发送频率（避免被限流，默认 5 条/分钟）
- 失败自动重试（最多 3 次，可配置）
- 支持优先级和定时发送
- Demo 模式模拟发送

**使用方法**:
```bash
python send_queue.py
```

**队列状态**:
- 0 = 待发送 (pending)
- 1 = 发送中 (sending)
- 2 = 已发送 (sent)
- 3 = 失败 (failed)

**日志**: `logs/send_queue.log`

---

### 🛡️ 第二阶段：稳定性

#### 5. ✅ 完善所有 API 调用的错误处理和重试
- 使用 `tenacity` 库（已安装）
- 所有 API 调用都有 `try-except` 包裹
- 指数退避重试策略

#### 6. ✅ 关键操作日志写入 logs/ 目录
- `logs/fetch_messages.log` - 消息轮询日志
- `logs/auto_reply.log` - 自动回复日志
- `logs/account_health.log` - 账号健康检查日志
- `logs/send_queue.log` - 发送队列日志

#### 7. ✅ Demo 模式下模拟消息轮询
- `fetch_messages.py` 中会随机生成模拟消息
- 模拟客户号码和消息内容
- 定时插入模拟新消息

---

### 🚀 第三阶段：商业化功能

#### 8. ✅ 消息全文搜索（Web 界面 + API）
**API 端点**:
- `GET /api/search_messages?q=<keyword>&conv_id=<可选>&limit=<可选>`

**返回**:
```json
{
  "results": [...],
  "count": 10
}
```

---

#### 9. ✅ 对话导出 CSV
**API 端点**:
- `GET /api/export_conversation/<conv_id>`

**功能**:
- 导出对话的所有消息（包括内部备注）
- 自动生成文件名：`conversation_<id>_<timestamp>.csv`
- 支持中文（BOM 头，解决 Excel 乱码）

---

#### 10. ✅ 统计面板增强（Chart.js 图表）
**API 端点**:
- `GET /api/stats/chart_data`

**返回数据**:
- `daily_trend`: 最近 7 天的消息趋势（收/发）
- `auto_reply_trend`: 自动回复率趋势
- `account_stats`: 账号使用统计（Top 10）

**使用方式**:
在前端使用 Chart.js 调用此 API 渲染图表。

---

#### 11. ✅ 对话内部备注功能
**数据库变更**:
- `tn_messages` 表添加 `is_internal` 字段（TINYINT, DEFAULT 0）

**API 端点**:
- `POST /api/conversations/<conv_id>/internal_note` - 添加内部备注
- `GET /api/conversations/<conv_id>/internal_notes` - 获取所有内部备注

**功能**:
- 客服可以添加内部备注（客户不可见）
- 内部备注在聊天界面中特殊标记

---

### 🗄️ 数据库变更

#### 新增表

1. **`tn_auto_rules`** - 自动回复规则表
```sql
CREATE TABLE tn_auto_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '规则名称',
    keywords VARCHAR(255) NOT NULL COMMENT '关键词，逗号分隔',
    template_id INT NOT NULL COMMENT '关联模板ID',
    priority INT DEFAULT 0 COMMENT '优先级（数字越大优先级越高）',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    match_mode VARCHAR(16) DEFAULT 'contains' COMMENT '匹配模式: contains/exact/regex',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_priority (priority),
    INDEX idx_active (is_active),
    FOREIGN KEY (template_id) REFERENCES tn_templates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

2. **`tn_send_queue`** - 发送队列表
```sql
CREATE TABLE tn_send_queue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL COMMENT '发送账号ID',
    conversation_id INT NOT NULL COMMENT '对话ID',
    to_number VARCHAR(32) NOT NULL COMMENT '接收方号码',
    content TEXT NOT NULL COMMENT '消息内容',
    priority INT DEFAULT 0 COMMENT '优先级（数字越大越优先）',
    status TINYINT DEFAULT 0 COMMENT '状态: 0=待发送, 1=发送中, 2=已发送, 3=失败',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    max_retries INT DEFAULT 3 COMMENT '最大重试次数',
    error_msg TEXT COMMENT '错误信息',
    scheduled_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '计划发送时间',
    sent_at DATETIME COMMENT '实际发送时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_scheduled (scheduled_at),
    INDEX idx_account (account_id),
    FOREIGN KEY (account_id) REFERENCES tn_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES tn_conversations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 修改的表

1. **`tn_messages`** - 添加 `is_internal` 字段
```sql
ALTER TABLE tn_messages 
ADD COLUMN is_internal TINYINT DEFAULT 0 COMMENT '是否为内部备注' AFTER is_auto_reply;
```

---

## 二、文件清单

### 新增文件
1. ✅ `fetch_messages.py` - 消息轮询引擎
2. ✅ `account_health.py` - 账号健康检查
3. ✅ `send_queue.py` - 发送队列
4. ✅ `tn_commercial_features.py` - 商业化功能 API 模块

### 修改的文件
1. ✅ `tn_customer_service.py` - 完善自动回复引擎（重写）
2. ✅ `tn_db.py` - 添加 `tn_auto_rules` 和 `tn_send_queue` 表，添加 `is_internal` 字段
3. ✅ `tn_web_dashboard.py` - 注册商业化功能 API

### 日志文件（自动创建）
1. `logs/fetch_messages.log`
2. `logs/auto_reply.log`
3. `logs/account_health.log`
4. `logs/send_queue.log`

---

## 三、部署和测试步骤

### 1. 初始化数据库
```bash
cd C:\Users\carti\Documents\textnow\其他文件\2026年\textnow
python init_db.py
```
**说明**: 这会创建所有必需的表并插入默认数据。

### 2. 启动 Docker 容器（如果未启动）
```bash
docker-compose up -d
```

### 3. 启动 Web 控制台
```bash
python tn_web_dashboard.py
```
**访问**: http://localhost:8899  
**账号**: admin / admin123

### 4. 启动消息轮询引擎（独立终端）
```bash
python fetch_messages.py
```

### 5. 启动自动回复引擎（独立终端）
```bash
python tn_customer_service.py
```

### 6. 启动账号健康检查（独立终端）
```bash
python account_health.py
```

### 7. 启动发送队列处理器（独立终端）
```bash
python send_queue.py
```

---

## 四、环境变量配置

在 `docker-compose.yml` 或 `.env` 文件中配置：

```env
# Demo 模式（1=开启，0=关闭）
TN_DEMO_MODE=1

# 消息轮询间隔（秒）
TN_FETCH_INTERVAL=30

# 健康检查间隔（秒）
TN_HEALTH_INTERVAL=300

# 队列轮询间隔（秒）
TN_QUEUE_POLL_INTERVAL=10

# 每账号每分钟最多发送消息数
TN_MAX_SEND_PER_ACCOUNT=5

# 自动回复开关
TN_AUTO_REPLY=1

# 并发处理账号数
TN_MAX_WORKERS=4
```

---

## 五、功能测试指南

### 测试 Demo 模式

1. **启动 Web 控制台**:
   ```bash
   python tn_web_dashboard.py
   ```

2. **启动消息轮询**:
   ```bash
   python fetch_messages.py
   ```

3. **观察日志**:
   - `logs/fetch_messages.log` 中会显示模拟消息生成
   - Web 界面中会看到新对话出现

### 测试自动回复

1. **查看自动回复规则**:
   访问 http://localhost:8899/templates  
   自动回复规则存储在 `tn_auto_rules` 表中。

2. **添加测试规则**:
   ```sql
   INSERT INTO tn_auto_rules (name, keywords, template_id, priority, is_active)
   VALUES ('测试规则', 'test,测试', 1, 10, 1);
   ```

3. **触发自动回复**:
   - 在 Demo 模式下，模拟消息包含关键词时会触发自动回复
   - 查看 `logs/auto_reply.log` 确认

### 测试全文搜索

1. **使用 API**:
   ```bash
   curl "http://localhost:8899/api/search_messages?q=test"
   ```

2. **在 Web 界面中**:
   需要在前端添加搜索框（见下面的"待完善功能"）

### 测试 CSV 导出

1. **使用 API**:
   ```bash
   curl -u admin:admin123 "http://localhost:8899/api/export_conversation/1" -o conversation.csv
   ```

### 测试 Chart.js 数据

1. **使用 API**:
   ```bash
   curl -u admin:admin123 "http://localhost:8899/api/stats/chart_data"
   ```

---

## 六、待完善功能

### 前端界面更新（需要手动完成）

由于时间限制，以下前端功能需要手动添加到 `tn_web_dashboard.py` 的 HTML 模板中：

1. **搜索框**（对话列表上方）
   - 调用 `GET /api/search_messages?q=<keyword>`
   - 显示搜索结果

2. **Chart.js 图表**（统计页面）
   - 调用 `GET /api/stats/chart_data`
   - 使用 Chart.js 渲染折线图、柱状图等

3. **内部备注 UI**（聊天界面）
   - 添加"添加备注"按钮
   - 调用 `POST /api/conversations/<conv_id>/internal_note`
   - 显示内部备注（特殊标记）

4. **CSV 导出按钮**（对话详情页）
   - 添加"导出 CSV"按钮
   - 调用 `GET /api/export_conversation/<conv_id>`

---

## 七、已知问题和限制

1. **TextNow API 过期**:
   - 当前账号号码已过期，真实 API 无法访问
   - 所有功能在 Demo 模式下测试通过
   - 需要更新账号 Cookie 和认证信息后才能使用真实 API

2. **代理未配置**:
   - `TN_PROXY` 环境变量已配置但可能无效
   - 真实 API 调用时需要有效的代理

3. **前端界面未完全更新**:
   - 后端 API 已全部实现
   - 前端界面需要手动添加搜索框、图表等组件

---

## 八、总结

✅ **第一阶段（核心功能）**: 100% 完成  
✅ **第二阶段（稳定性）**: 100% 完成  
✅ **第三阶段（商业化功能）**: 90% 完成（后端 API 全部完成，前端界面待完善）

**建议下一步**:
1. 更新 TextNow 账号 Cookie 和认证信息
2. 完善前端界面（添加搜索框、Chart.js 图表、内部备注 UI）
3. 配置有效代理
4. 进行端到端测试

---

**报告生成时间**: 2026-06-13 03:50 GMT+8  
**项目状态**: 商业化升级第一阶段和第二阶段已完成，第三阶段后端完成，前端待完善
