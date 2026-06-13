with open('tn_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for CREATE TABLE statements
import re
creates = re.findall(r'CREATE TABLE.*?\(', content, re.DOTALL)
for c in creates:
    print(c[:100])
    print('---')
