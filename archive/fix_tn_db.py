#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 tn_db.py 中的表名（添加 tn_ 前缀）
"""

with open('tn_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复表名（按长度降序，避免重复替换）
replacements = [
    # FOREIGN KEY 引用
    ('REFERENCES accounts(id)', 'REFERENCES tn_accounts(id)'),
    ('REFERENCES conversations(id)', 'REFERENCES tn_conversations(id)'),
    # CREATE TABLE 语句
    ('CREATE TABLE IF NOT EXISTS conversations (', 'CREATE TABLE IF NOT EXISTS tn_conversations ('),
    ('CREATE TABLE IF NOT EXISTS messages (', 'CREATE TABLE IF NOT EXISTS tn_messages ('),
    ('CREATE TABLE IF NOT EXISTS accounts (', 'CREATE TABLE IF NOT EXISTS tn_accounts ('),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'Fixed: {old} -> {new}')
    else:
        print(f'Not found: {old}')

# 保存
with open('tn_db.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\nFix complete')
