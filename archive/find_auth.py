with open('tn_web_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()
for term in ['401', 'WWW-Authenticate', 'authorization', 'before_request']:
    idx = content.find(term)
    if idx >= 0:
        print(f'FOUND "{term}" at {idx}: ...{content[max(0,idx-80):idx+80]}...')
    else:
        print(f'NOT FOUND: {term}')
