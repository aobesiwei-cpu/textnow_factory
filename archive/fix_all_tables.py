#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 tn_customer_service.py 中的表名 + 列名不匹配问题
同时修复 tn_web_dashboard.py 中遗留的问题
"""

import re

# ===================== 1. 修复 tn_customer_service.py =====================
with open('tn_customer_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements_cs = [
    # 表名
    ('FROM accounts', 'FROM tn_accounts'),
    ('FROM conversations', 'FROM tn_conversations'),
    ('INTO conversations', 'INTO tn_conversations'),
    ('UPDATE conversations', 'UPDATE tn_conversations'),
    ('FROM messages', 'FROM tn_messages'),
    ('INTO messages', 'INTO tn_messages'),
    ('UPDATE messages', 'UPDATE tn_messages'),
    ('FROM reply_templates', 'FROM tn_templates'),
    ('FROM cs_settings', 'FROM tn_settings'),
    ('INTO cs_settings', 'INTO tn_settings'),
    # 列名
    ('last_message_time', 'last_message_at'),
    ('sent_time', 'sent_at'),
    ('create_time', 'created_at'),
    ('created_time', 'created_at'),
]

for old, new in replacements_cs:
    content = content.replace(old, new)

with open('tn_customer_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("1. tn_customer_service.py - fixed")

# ===================== 2. 修复 tn_db.py 中的表名 =====================
with open('tn_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements_db = [
    ('CREATE TABLE IF NOT EXISTS reply_templates', 'CREATE TABLE IF NOT EXISTS tn_templates'),
    ('CREATE TABLE IF NOT EXISTS cs_settings', 'CREATE TABLE IF NOT EXISTS tn_settings'),
    ('INSERT IGNORE INTO reply_templates', 'INSERT IGNORE INTO tn_templates'),
    ('INSERT IGNORE INTO cs_settings', 'INSERT IGNORE INTO tn_settings'),
    ('SELECT content FROM reply_templates', 'SELECT content FROM tn_templates'),
    ("SELECT `value` FROM cs_settings", "SELECT `value` FROM tn_settings"),
]

for old, new in replacements_db:
    content = content.replace(old, new)

with open('tn_db.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("2. tn_db.py - fixed")

# ===================== 3. 添加缺失的 tn_settings 表到 init_db.py =====================
with open('init_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'tn_settings' not in content:
    # 在 CREATE_AUTO_RULES 后面添加 tn_settings 表
    settings_table = """

CREATE_SETTINGS = \"\"\"
CREATE TABLE IF NOT EXISTS tn_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(64) NOT NULL UNIQUE,
    `value` TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
\"\"\"
"""
    # 在 CREATE_AUTO_RULES 定义之后插入
    content = content.replace(
        'CREATE_AUTO_RULES = """',
        settings_table + 'CREATE_AUTO_RULES = """'
    )
    # 在建表部分添加执行
    content = content.replace(
        '    cur.execute(CREATE_AUTO_RULES)\n    print("',
        '    cur.execute(CREATE_SETTINGS)\n    print("   [OK] tn_settings")\n    cur.execute(CREATE_AUTO_RULES)\n    print("'
    )
    # 添加默认设置数据
    content = content.replace(
        '    if insert_samples:\n        insert_sample_data(conn)',
        '''    if insert_samples:
        insert_sample_data(conn)
    
    # Insert default settings
    cur = conn.cursor()
    default_settings = [
        ('auto_reply_enabled', '1'),
        ('auto_reply_template', '/auto'),
        ('poll_interval', '15'),
        ('max_concurrent_chats', '5'),
        ('work_start_hour', '9'),
        ('work_end_hour', '21'),
    ]
    for key, val in default_settings:
        cur.execute(
            "INSERT IGNORE INTO tn_settings (`key`, `value`) VALUES (%s,%s)",
            (key, val)
        )
    conn.commit()
    print("   [OK] Default settings inserted")'''
    )

with open('init_db.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("3. init_db.py - added tn_settings table")

print("\nAll fixes applied!")
