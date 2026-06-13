#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 tn_web_dashboard.py 中的表名和列名"""

import re

# 读取文件
with open('tn_web_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换表名
replacements = [
    # 表名
    ('FROM conversations', 'FROM tn_conversations'),
    ('JOIN conversations', 'JOIN tn_conversations'),
    ('LEFT JOIN conversations', 'LEFT JOIN tn_conversations'),
    ('UPDATE conversations', 'UPDATE tn_conversations'),
    ('INSERT INTO conversations', 'INSERT INTO tn_conversations'),
    ('DELETE FROM conversations', 'DELETE FROM tn_conversations'),
    
    ('FROM messages', 'FROM tn_messages'),
    ('JOIN messages', 'JOIN tn_messages'),
    ('LEFT JOIN messages', 'LEFT JOIN tn_messages'),
    ('UPDATE messages', 'UPDATE tn_messages'),
    ('INSERT INTO messages', 'INSERT INTO tn_messages'),
    ('DELETE FROM messages', 'DELETE FROM tn_messages'),
    
    ('FROM accounts', 'FROM tn_accounts'),
    ('JOIN accounts', 'JOIN tn_accounts'),
    ('LEFT JOIN accounts', 'LEFT JOIN tn_accounts'),
    ('UPDATE accounts', 'UPDATE tn_accounts'),
    ('INSERT INTO accounts', 'INSERT INTO tn_accounts'),
    ('DELETE FROM accounts', 'DELETE FROM tn_accounts'),
    
    ('FROM reply_templates', 'FROM tn_templates'),
    ('JOIN reply_templates', 'JOIN tn_templates'),
    ('LEFT JOIN reply_templates', 'LEFT JOIN tn_templates'),
    ('UPDATE reply_templates', 'UPDATE tn_templates'),
    ('INSERT INTO reply_templates', 'INSERT INTO tn_templates'),
    ('DELETE FROM reply_templates', 'DELETE FROM tn_templates'),
    
    ('FROM auto_rules', 'FROM tn_auto_rules'),
    ('JOIN auto_rules', 'JOIN tn_auto_rules'),
    ('LEFT JOIN auto_rules', 'LEFT JOIN tn_auto_rules'),
    ('UPDATE auto_rules', 'UPDATE tn_auto_rules'),
    ('INSERT INTO auto_rules', 'INSERT INTO tn_auto_rules'),
    ('DELETE FROM auto_rules', 'DELETE FROM tn_auto_rules'),
    
    # 列名
    ('last_message_time', 'last_message_at'),
    ('sent_time', 'sent_at'),
    ('create_time', 'created_at'),
]

# 执行替换
for old, new in replacements:
    content = content.replace(old, new)

# 写回文件
with open('tn_web_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已修复所有表名和列名（UTF-8 编码保持完整）")
print(f"📝 共替换 {len(replacements)} 种模式")
