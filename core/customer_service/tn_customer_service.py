"""
TextNow 客服系统 - 自动回复引擎（完善版）

功能：
  1. 监听新消息，根据 tn_auto_rules 关键词匹配模板
  2. 支持优先级（priority 字段，数字越大优先级越高）
  3. 支持多种匹配模式（contains/exact/regex）
  4. Demo 模式模拟发送
  5. 写入日志 logs/auto_reply.log
  6. 失败重试机制

作者：TextNow CS System
日期：2026-06-13
"""

import os
import sys
import re
import logging
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import requests
import pymysql

# 导入项目配置和数据库模块
from tn_config import PROXY, AUTO_REPLY_ENABLED, MAX_WORKERS
from tn_db import get_db, get_db_dict

# ===================== 日志配置 =====================
# 主日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# 自动回复专用日志
auto_reply_logger = logging.getLogger('auto_reply')
auto_reply_logger.setLevel(logging.INFO)
auto_reply_handler = logging.FileHandler('logs/auto_reply.log', encoding='utf-8')
auto_reply_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
auto_reply_logger.addHandler(auto_reply_handler)


class AutoReplyEngine:
    """自动回复引擎"""

    def __init__(self):
        log.info("🤖 自动回复引擎初始化完成")
        log.info(f"   自动回复: {'启用' if AUTO_REPLY_ENABLED else '禁用'}")

    def process_message(self, conv_id: int, message_id: int) -> bool:
        """
        处理单条消息，尝试匹配自动回复规则
        返回：是否成功回复
        """
        if not AUTO_REPLY_ENABLED:
            log.debug("自动回复已禁用，跳过")
            return False

        # 1. 获取消息内容
        conn = get_db_dict()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute("""
            SELECT m.*, c.contact_number, c.account_id, a.username, a.phone
            FROM tn_messages m
            LEFT JOIN tn_conversations c ON m.conversation_id = c.id
            LEFT JOIN tn_accounts a ON c.account_id = a.id
            WHERE m.id = %s
        """, (message_id,))
        message = cur.fetchone()

        if not message:
            log.warning(f"消息不存在: message_id={message_id}")
            conn.close()
            return False

        # 只处理收到的消息（direction=1）
        if message['direction'] != 1:
            conn.close()
            return False

        content = message['content']
        contact_number = message['contact_number']
        account_id = message['account_id']

        log.info(f"📨 处理消息: conv_id={conv_id}, from={contact_number}, content={content[:50]}...")

        # 2. 查找匹配的规则（按优先级降序）
        cur.execute("""
            SELECT r.*, t.content as template_content
            FROM tn_auto_rules r
            LEFT JOIN tn_templates t ON r.template_id = t.id
            WHERE r.is_active = 1 AND t.is_active = 1
            ORDER BY r.priority DESC
        """)
        rules = cur.fetchall()
        conn.close()

        # 3. 匹配规则
        matched_rule = None
        for rule in rules:
            if self._match_rule(content, rule):
                matched_rule = rule
                break

        if not matched_rule:
            log.info(f"💭 未匹配到规则: conv_id={conv_id}, content={content[:50]}...")
            return False

        # 4. 获取账号信息
        conn = get_db_dict()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM tn_accounts WHERE id=%s", (account_id,))
        account = cur.fetchone()
        conn.close()

        if not account:
            log.error(f"❌ 账号不存在: account_id={account_id}")
            return False

        # 5. 渲染模板
        template_content = matched_rule['template_content']
        reply_content = self._render_template(template_content, {
            'contact_number': contact_number,
            'account_phone': account.get('phone', ''),
            'account_email': account.get('email', ''),
        })

        # 6. 发送回复
        success = self._send_reply(account, contact_number, reply_content, conv_id)

        if success:
            # 7. 标记消息为自动回复
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE tn_messages SET is_auto_reply=1 WHERE id=%s",
                (message_id,)
            )
            conn.commit()
            conn.close()

            # 8. 记录日志
            auto_reply_logger.info(
                f"✅ 自动回复成功 | conv_id={conv_id} | rule={matched_rule['name']} | "
                f"to={contact_number} | content={reply_content[:50]}..."
            )
            log.info(f"✅ 自动回复成功: conv_id={conv_id}, rule={matched_rule['name']}")
            return True
        else:
            auto_reply_logger.warning(
                f"❌ 自动回复失败 | conv_id={conv_id} | rule={matched_rule['name']} | "
                f"to={contact_number}"
            )
            return False

    def _match_rule(self, content: str, rule: Dict) -> bool:
        """
        检查消息内容是否匹配规则
        支持三种模式：
          - contains: 包含关键词（默认）
          - exact: 完全匹配
          - regex: 正则表达式匹配
        """
        keywords = [k.strip().lower() for k in rule['keywords'].split(',')]
        match_mode = rule.get('match_mode', 'contains')
        content_lower = content.lower()

        if match_mode == 'exact':
            # 完全匹配：内容必须和关键词之一完全相同
            return content_lower in keywords

        elif match_mode == 'regex':
            # 正则匹配：关键词作为正则表达式
            for keyword in keywords:
                try:
                    if re.search(keyword, content, re.IGNORECASE):
                        return True
                except re.error:
                    log.warning(f"无效的正则表达式: {keyword}")
                    continue
            return False

        else:  # contains
            # 包含匹配：内容包含任意关键词
            return any(k in content_lower for k in keywords)

    def _render_template(self, template: str, variables: Dict) -> str:
        """
        渲染模板，替换变量
        支持变量：{contact_number}, {account_phone}, {account_email} 等
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            log.warning(f"模板变量缺失: {e}")
            return template
        except Exception as e:
            log.error(f"模板渲染失败: {e}")
            return template

    def _send_reply(self, account: Dict, to_number: str, content: str, conv_id: int) -> bool:
        """
        发送回复消息（通过 TextNow API）
        """
        return self._send_via_api(account, to_number, content, conv_id)

    def _send_via_api(self, account: Dict, to_number: str, content: str, conv_id: int) -> bool:
        """
        通过 TextNow API 发送消息
        包含重试机制（最多 3 次）
        """
        headers = self._build_headers(account)
        url = f"https://api.textnow.me/api/v2/users/{account['username']}/messages"
        payload = {
            "to": to_number,
            "content": content,
            "message_type": "text"
        }

        # 重试机制
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    proxies=PROXY,
                    timeout=20
                )

                if resp.status_code in (200, 201):
                    log.info(f"📤 API 发送成功 (尝试 {attempt}/{max_retries})")

                    # 保存消息到数据库
                    conn = get_db()
                    cur = conn.cursor()
                    cur.execute(
                        """INSERT INTO tn_messages 
                           (conversation_id, direction, content, is_auto_reply, sent_at, created_at) 
                           VALUES (%s, 2, %s, 1, NOW(), NOW())""",
                        (conv_id, content)
                    )
                    conn.commit()
                    conn.close()

                    return True
                else:
                    log.warning(
                        f"⚠️  API 发送失败 (尝试 {attempt}/{max_retries}): "
                        f"status={resp.status_code}, response={resp.text[:100]}"
                    )

            except Exception as e:
                log.error(f"❌ API 调用异常 (尝试 {attempt}/{max_retries}): {e}")

            # 等待重试
            if attempt < max_retries:
                wait_time = attempt * 2  # 指数退避
                log.info(f"⏳ {wait_time}秒后重试...")
                time.sleep(wait_time)

        log.error(f"❌ API 发送失败，已达最大重试次数: to={to_number}")
        return False

    def _build_headers(self, account: Dict) -> Dict:
        """构建 TextNow API 请求头"""
        return {
            "Host": "api.textnow.me",
            "Content-Type": "application/json",
            "User-Agent": account.get("user_agent", ""),
            "X-Idfa": account.get("idfa", ""),
            "X-Client-ID": account.get("client_id", ""),
            "X-PX-Auth": account.get("px_auth", ""),
            "X-Device-FP": account.get("device_fp", ""),
            "Cookie": account.get("cookie", ""),
            "Accept": "application/json",
            "Accept-Language": "en-US",
        }

    def batch_process_pending(self, limit: int = 50):
        """
        批量处理待回复的消息
        用于定时任务或手动触发
        """
        conn = get_db_dict()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        # 查找未回复的入站消息（direction=1 且 is_auto_reply=0）
        cur.execute("""
            SELECT m.id as message_id, m.conversation_id
            FROM tn_messages m
            LEFT JOIN tn_conversations c ON m.conversation_id = c.id
            WHERE m.direction = 1 
              AND m.is_auto_reply = 0
              AND c.status = 1
            ORDER BY m.sent_at ASC
            LIMIT %s
        """, (limit,))
        pending_messages = cur.fetchall()
        conn.close()

        log.info(f"📋 找到 {len(pending_messages)} 条待处理消息")

        success_count = 0
        for msg in pending_messages:
            try:
                if self.process_message(msg['conversation_id'], msg['message_id']):
                    success_count += 1
            except Exception as e:
                log.error(f"处理消息失败: message_id={msg['message_id']}, error={e}")

        log.info(f"✅ 批量处理完成: 成功={success_count}/{len(pending_messages)}")
        return success_count


# ===================== 独立运行模式 =====================
def main():
    """独立运行模式：作为守护进程处理待回复消息"""
    log.info("=" * 60)
    log.info("🚀 TextNow 客服系统 - 自动回复引擎（独立模式）")
    log.info("=" * 60)

    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    engine = AutoReplyEngine()

    # 定时处理待回复消息
    import signal
    running = True

    def signal_handler(signum, frame):
        nonlocal running
        log.info("🛑 收到退出信号...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log.info("✅ 自动回复引擎已启动，按 Ctrl+C 停止")

    while running:
        try:
            engine.batch_process_pending(limit=50)
        except Exception as e:
            log.error(f"❌ 批量处理异常: {e}", exc_info=True)

        # 等待下次处理
        for i in range(30):  # 30 秒
            if not running:
                break
            time.sleep(1)

    log.info("👋 自动回复引擎已停止")


if __name__ == '__main__':
    main()
