#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给 tn_web_dashboard.py 打补丁（无 emoji 版本）
用法：python patch_auth_system.py
"""
import os, re, hashlib

BASE = r"C:\Users\carti\Documents\textnow\其他文件\2026年\textnow"
py_file = os.path.join(BASE, "tn_web_dashboard.py")
bak_file = py_file + ".bak"

with open(py_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 备份
with open(bak_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("[OK] 已备份到 {}".format(bak_file))

# ─── 1. imports 加 hashlib ───
if 'import hashlib' not in content:
    content = content.replace('import pymysql\n', 'import pymysql\nimport hashlib\n', 1)
    print("[OK] 已添加 import hashlib")

# ─── 2. 加 app.secret_key ───
if 'app.secret_key' not in content:
    content = content.replace(
        'app = Flask(__name__)\n',
        'app = Flask(__name__)\napp.secret_key = os.getenv("TN_SECRET_KEY", "textnow-cs-secret-key-2026")\n',
        1
    )
    print("[OK] 已添加 app.secret_key")

# ─── 3. 替换 Basic Auth 为 session 登录 ───
old_block = '''# ===================== Basic Auth =====================
def check_auth(username, password):
    """验证用户名密码"""
    return username == WEB_USER and password == WEB_PASS


def authenticate():
    """返回 401 响应要求认证"""
    return Response(
        '需要登录才能访问\\n请使用正确的用户名和密码',
        401,
        {'WWW-Authenticate': 'Basic realm="TextNow CS"'}
    )


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return wrapper'''

new_block = '''# ===================== Session 登录验证 =====================
def verify_agent(username, password):
    """验证坐席账号（数据库 tn_agents 表）"""
    try:
        from tn_db import get_db, get_db_dict
        import pymysql
        conn = get_db_dict()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT id, username, password_hash, role, nickname, is_active FROM tn_agents WHERE username=%s", (username,))
        agent = cur.fetchone()
        conn.close()
        if not agent:
            return None, "账号不存在"
        if not agent["is_active"]:
            return None, "账号已被禁用"
        pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if pwd_hash != agent["password_hash"]:
            return None, "密码错误"
        return agent, None
    except Exception as e:
        return None, str(e)


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "agent_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper'''

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("[OK] 已替换登录验证为 session 方式")
else:
    print("[WARN] 未找到 Basic Auth 代码块，跳过")

# ─── 4. 在路由区前插入登录/登出路由和 require_role ───
login_code = '''

# ===================== 登录 / 登出 =====================
LOGIN_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>登录 - TextNow 客服系统</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#001529;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#fff;padding:32px 40px;border-radius:8px;width:320px;box-shadow:0 4px 20px rgba(0,0,0,.15)}
h2{margin:0 0 20px;color:#001529;text-align:center}
input{width:100%;padding:8px 12px;border:1px solid #d9d9d9;border-radius:4px;font-size:14px;margin-bottom:14px;box-sizing:border-box}
.btn{width:100%;padding:8px;border:none;border-radius:4px;background:#1890ff;color:#fff;font-size:14px;cursor:pointer}
.error{color:#ff4d4f;font-size:12px;margin-bottom:10px;text-align:center}
.footer{text-align:center;color:#999;font-size:11px;margin-top:16px}
</style></head><body>
<div class="box"><h2>TextNow 客服系统</h2>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST"><input name="username" placeholder="用户名" required autofocus>
<input name="password" type="password" placeholder="密码" required>
<button class="btn">登 录</button></form>
<div class="footer">默认超管：admin / admin123</div>
</div></body></html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return render_template_string(LOGIN_HTML, error="请输入用户名和密码")
        agent, err = verify_agent(username, password)
        if err:
            return render_template_string(LOGIN_HTML, error=err)
        session["agent_id"]   = agent["id"]
        session["agent_role"]  = agent["role"]
        session["agent_user"]   = agent["username"]
        session["agent_name"]   = agent["nickname"] or agent["username"]
        try:
            from tn_db import get_db
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE tn_agents SET last_login_time=NOW() WHERE id=%s", (agent["id"],))
            conn.commit()
            conn.close()
        except:
            pass
        return redirect("/")
    return render_template_string(LOGIN_HTML, error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ===================== 角色权限装饰器 =====================
def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("agent_role") not in allowed_roles:
                return jsonify({"success": False, "error": "无权操作"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

'''

if '# ===================== 路由 =====================' in content and 'def login():' not in content:
    content = content.replace(
        '# ===================== 路由 =====================',
        login_code + '# ===================== 路由 =====================',
        1
    )
    print("[OK] 已插入登录/登出路由和 require_role")
else:
    print("[WARN] 路由区已存在登录代码或找不到标记，跳过")

# ─── 5. 修改 index 路由，注入 agent 变量 ───
old_render = 'demo_mode=DEMO_MODE,'
new_render = 'agent_id=session.get("agent_id"), agent_role=session.get("agent_role",""), agent_name=session.get("agent_name",""), is_admin=(session.get("agent_role")=="admin"), demo_mode=DEMO_MODE,'
if old_render in content:
    content = content.replace(old_render, new_render, 1)
    print("[OK] 已给 index 路由注入 agent 变量")
else:
    print("[WARN] 未找到 demo_mode=DEMO_MODE 标记，需手动检查 index 路由")

# ─── 6. 修改 INDEX_HTML 导航栏 ───
old_nav = '''<div class="navbar">
  <h1>TextNow 客服系统</h1>
  <a href="/" style="color:#aaa; text-decoration:none; font-size:13px;">💬 对话</a>
  <a href="/accounts" style="color:#aaa; text-decoration:none; font-size:13px;">📋 账号</a>
  <a href="/templates" style="color:#aaa; text-decoration:none; font-size:13px;">📝 模板</a>
  <a href="/stats" style="color:#aaa; text-decoration:none; font-size:13px;">📊 统计</a>
  <div class="status">
    <div class="status-dot"></div>
    <span>服务运行中</span>
  </div>
</div>'''

new_nav = '''<div class="navbar">
  <h1>TextNow 客服系统</h1>
  <a href="/" style="color:#aaa; text-decoration:none; font-size:13px;">对话</a>
  <a href="/accounts" style="color:#aaa; text-decoration:none; font-size:13px;">账号</a>
  {% if agent_role == "admin" %}
  <a href="/agents" style="color:#aaa; text-decoration:none; font-size:13px;">坐席</a>
  <a href="/assign" style="color:#aaa; text-decoration:none; font-size:13px;">分配</a>
  {% endif %}
  <a href="/templates" style="color:#aaa; text-decoration:none; font-size:13px;">模板</a>
  <a href="/stats" style="color:#aaa; text-decoration:none; font-size:13px;">统计</a>
  <div style="margin-left:auto;display:flex;align-items:center;gap:12px">
    <span style="color:#aaa;font-size:12px">{{ agent_name }}（{{ "超管" if agent_role=="admin" else "坐席" }}）</span>
    <a href="/logout" style="color:#ff7875;font-size:12px;text-decoration:none">退出</a>
  </div>
</div>'''

if old_nav in content:
    content = content.replace(old_nav, new_nav, 1)
    print("[OK] 已更新导航栏（用户信息 + 退出）")
else:
    print("[WARN] 未找到导航栏代码，跳过")

# ─── 7. 在 if __name__ == "__main__" 前插入坐席管理和分配路由 ───
agent_code = r'''

# ===================== 坐席管理（仅 admin）=====================
AGENTS_HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>坐席管理 - TextNow 客服系统</title>
<style>
body{font-family:-apple-system,sans-serif;background:#f0f2f5;margin:0}
.nav{background:#001529;color:#fff;padding:0 24px;display:flex;align-items:center;height:48px}
.nav a{color:#ffffffcc;text-decoration:none;margin-right:20px;font-size:13px}
.nav .user{margin-left:auto;color:#ffffffcc;font-size:13px}
.nav .logout{color:#ff7875;margin-left:12px;text-decoration:none}
h2{margin:16px 0 8px;font-size:15px;color:#333}
.table{width:100%;border-collapse:collapse;background:#fff;font-size:13px}
.table th,.table td{padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:left}
.table th{background:#fafafa;font-weight:600;color:#666}
.btn{padding:4px 12px;border:none;border-radius:4px;cursor:pointer;font-size:12px}
.btn-primary{background:#1890ff;color:#fff}
.btn-danger{background:#ff4d4f;color:#fff}
.btn-sm{padding:2px 8px;font-size:11px}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);z-index:1000;justify-content:center;align-items:center}
.modal.show{display:flex}
.modal-box{background:#fff;border-radius:8px;padding:24px;width:400px;max-width:90vw}
.modal-box input,.modal-box select{width:100%;padding:6px 10px;border:1px solid #d9d9d9;border-radius:4px;font-size:13px;margin-bottom:12px}
</style></head><body>
<div class="nav">
  <a href="/">对话</a><a href="/accounts">账号</a>
  <a href="/agents" style="color:#fff">坐席</a>
  <a href="/templates">模板</a><a href="/stats">统计</a>
  <span class="user">{{ agent_name }}</span>
  <a href="/logout" class="logout">退出</a>
</div>
<div style="padding:16px 24px">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2 style="margin:0">坐席管理</h2>
    <button class="btn btn-primary" onclick="openModal()">+ 添加坐席</button>
  </div>
  <table class="table" style="margin-top:12px">
    <tr><th>ID</th><th>用户名</th><th>昵称</th><th>角色</th><th>状态</th><th>最后登录</th><th>操作</th></tr>
    {% for a in agents %}
    <tr>
      <td>{{ a.id }}</td>
      <td>{{ a.username }}</td>
      <td>{{ a.nickname or '-' }}</td>
      <td>{% if a.role=='admin' %}超管{% elif a.role=='agent' %}坐席{% else %}只读{% endif %}</td>
      <td>{% if a.is_active %}启用{% else %}禁用{% endif %}</td>
      <td>{{ a.last_login_time_str or '-' }}</td>
      <td>
        <button class="btn btn-sm btn-primary" onclick="editAgent({{ a.id }},'{{ a.username }}','{{ a.nickname or '' }}','{{ a.role }}',{{ 'true' if a.is_active else 'false' }})">编辑</button>
        {% if a.id != agent_id %}<button class="btn btn-sm btn-danger" onclick="delAgent({{ a.id }},'{{ a.username }}')">删除</button>{% endif %}
      </td>
    </tr>
    {% endfor %}
  </table>
</div>
<div class="modal" id="modal"><div class="modal-box">
  <h3 id="modalTitle">添加坐席</h3>
  <input type="hidden" id="editId">
  <label>用户名<br><input id="inpUsername" style="width:100%"></label><br><br>
  <label>昵称<br><input id="inpNickname" style="width:100%"></label><br><br>
  <label>密码（留空=不修改）<br><input id="inpPassword" type="password" style="width:100%"></label><br><br>
  <label>角色<br><select id="inpRole" style="width:100%;padding:6px">
    <option value="agent">坐席</option><option value="admin">超管</option><option value="viewer">只读</option>
  </select></label><br><br>
  <label><input type="checkbox" id="inpActive" checked> 启用</label><br><br>
  <div style="text-align:right">
    <button class="btn" onclick="closeModal()">取消</button>
    <button class="btn btn-primary" onclick="saveAgent()">保存</button>
  </div>
</div></div>
<script>
function openModal(){document.getElementById('modalTitle').textContent='添加坐席';document.getElementById('editId').value='';document.getElementById('inpUsername').value='';document.getElementById('inpNickname').value='';document.getElementById('inpPassword').value='';document.getElementById('inpRole').value='agent';document.getElementById('inpActive').checked=true;document.getElementById('modal').classList.add('show')}
function closeModal(){document.getElementById('modal').classList.remove('show')}
function editAgent(id,user,nick,role,isActive){document.getElementById('modalTitle').textContent='编辑坐席';document.getElementById('editId').value=id;document.getElementById('inpUsername').value=user;document.getElementById('inpNickname').value=nick;document.getElementById('inpRole').value=role;document.getElementById('inpActive').checked=isActive;document.getElementById('modal').classList.add('show')}
async function saveAgent(){const id=document.getElementById('editId').value;const body={username:document.getElementById('inpUsername').value.trim(),nickname:document.getElementById('inpNickname').value.trim(),role:document.getElementById('inpRole').value,is_active:document.getElementById('inpActive').checked?1:0};const pwd=document.getElementById('inpPassword').value;if(pwd)body.password=pwd;if(!body.username){alert('请输入用户名');return}const url=id?`/api/agents/${id}`:'/api/agents';const r=await fetch(url,{method:id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const j=await r.json();if(j.success){location.reload()}else{alert('错误：'+j.error)}}
async function delAgent(id,name){if(!confirm('确定删除坐席「'+name+'」？'))return;const r=await fetch(`/api/agents/${id}`,{method:'DELETE'});const j=await r.json();if(j.success){location.reload()}else{alert('错误：'+j.error)}}
</script></body></html>"""

@app.route("/agents")
@requires_auth
@require_role("admin")
def page_agents():
    from tn_db import get_db, get_db_dict
    import pymysql
    conn = get_db_dict()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT *,DATE_FORMAT(last_login_time,'%%Y-%%m-%%d %%H:%%i') as last_login_time_str FROM tn_agents ORDER BY id ASC")
    agents = cur.fetchall()
    conn.close()
    return render_template_string(AGENTS_HTML, agents=agents,
        agent_id=session.get("agent_id"), agent_name=session.get("agent_name",""))

@app.route("/api/agents", methods=["POST"])
@requires_auth
@require_role("admin")
def api_add_agent():
    import pymysql
    data = request.get_json()
    username   = data.get("username","").strip()
    password   = data.get("password","")
    nickname   = data.get("nickname","")
    role       = data.get("role","agent")
    is_active  = data.get("is_active",1)
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"})
    if role not in ("admin","agent","viewer"):
        return jsonify({"success": False, "error": "无效的角色"})
    pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    try:
        from tn_db import get_db
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO tn_agents (username,password_hash,nickname,role,is_active) VALUES (%s,%s,%s,%s,%s)",
            (username, pwd_hash, nickname, role, is_active))
        conn.commit(); conn.close()
        return jsonify({"success": True})
    except pymysql.err.IntegrityError:
        return jsonify({"success": False, "error": "用户名已存在"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/agents/<int:agent_id>", methods=["PUT"])
@requires_auth
@require_role("admin")
def api_edit_agent(agent_id):
    import pymysql
    data = request.get_json()
    nickname   = data.get("nickname","")
    role       = data.get("role","agent")
    is_active  = data.get("is_active",1)
    password   = data.get("password","")
    if role not in ("admin","agent","viewer"):
        return jsonify({"success": False, "error": "无效的角色"})
    try:
        from tn_db import get_db
        conn = get_db(); cur = conn.cursor()
        if password:
            pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            cur.execute("UPDATE tn_agents SET nickname=%s,role=%s,is_active=%s,password_hash=%s WHERE id=%s",
                (nickname, role, is_active, pwd_hash, agent_id))
        else:
            cur.execute("UPDATE tn_agents SET nickname=%s,role=%s,is_active=%s WHERE id=%s",
                (nickname, role, is_active, agent_id))
        conn.commit(); conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/agents/<int:agent_id>", methods=["DELETE"])
@requires_auth
@require_role("admin")
def api_del_agent(agent_id):
    if agent_id == session.get("agent_id"):
        return jsonify({"success": False, "error": "不能删除自己"})
    try:
        from tn_db import get_db
        conn = get_db(); cur = conn.cursor()
        cur.execute("DELETE FROM tn_agents WHERE id=%s", (agent_id,))
        conn.commit(); conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ===================== 账号分配（仅 admin）=====================
ASSIGN_HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>账号分配 - TextNow 客服系统</title>
<style>
body{font-family:-apple-system,sans-serif;background:#f0f2f5;margin:0}
.nav{background:#001529;color:#fff;padding:0 24px;display:flex;align-items:center;height:48px}
.nav a{color:#ffffffcc;text-decoration:none;margin-right:20px;font-size:13px}
.nav .user{margin-left:auto;color:#ffffffcc;font-size:13px}
.nav .logout{color:#ff7875;margin-left:12px;text-decoration:none}
h2{margin:16px 0 4px;font-size:15px;color:#333}
.desc{color:#999;font-size:12px;margin:0 0 12px}
.table{width:100%;border-collapse:collapse;background:#fff;font-size:13px}
.table th,.table td{padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:left}
.table th{background:#fafafa;font-weight:600;color:#666}
.btn{padding:4px 12px;border:none;border-radius:4px;cursor:pointer;font-size:12px}
.btn-primary{background:#1890ff;color:#fff}
.btn-sm{padding:2px 8px;font-size:11px}
select{padding:4px 8px;border:1px solid #d9d9d9;border-radius:4px}
</style></head><body>
<div class="nav">
  <a href="/">对话</a><a href="/accounts">账号</a>
  <a href="/agents">坐席</a>
  <a href="/assign" style="color:#fff">分配</a>
  <a href="/templates">模板</a><a href="/stats">统计</a>
  <span class="user">{{ agent_name }}</span>
  <a href="/logout" class="logout">退出</a>
</div>
<div style="padding:16px 24px">
  <h2 style="margin:0">TextNow 账号分配</h2>
  <p class="desc">将 TextNow 账号分配给坐席，坐席只能使用分配给自己的账号收发消息</p>
  <table class="table">
    <tr><th>账号ID</th><th>用户名</th><th>手机号</th><th>状态</th><th>当前分配</th><th>操作</th></tr>
    {% for a in accounts %}
    <tr>
      <td>{{ a.id }}</td>
      <td>{{ a.username }}</td>
      <td>{{ a.phone or '-' }}</td>
      <td>{% if a.status %}可用{% else %}停用{% endif %}</td>
      <td>{{ a.agent_name or '（未分配）' }}</td>
      <td>
        <select id="sel_{{ a.id }}" style="padding:4px">
          <option value="">（未分配）</option>
          {% for ag in agents %}
          <option value="{{ ag.id }}" {% if ag.id==a.agent_id %}selected{% endif %}>{{ ag.nickname or ag.username }}</option>
          {% endfor %}
        </select>
        <button class="btn btn-sm btn-primary" onclick="assign({{ a.id }})">保存</button>
      </td>
    </tr>
    {% endfor %}
  </table>
</div>
<script>
async function assign(accountId){
  const sel=document.getElementById('sel_'+accountId);
  const agentId=sel.value||null;
  const body=agentId?{agent_id:parseInt(agentId)}:{agent_id:null};
  const res=await fetch(`/api/assign_account/${accountId}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const j=await res.json();
  if(j.success){location.reload()}else{alert('错误：'+j.error)}
}
</script></body></html>"""

@app.route("/assign")
@requires_auth
@require_role("admin")
def page_assign():
    from tn_db import get_db, get_db_dict
    import pymysql
    conn = get_db_dict()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""SELECT a.*, ag.nickname as agent_name, aa.agent_id
        FROM accounts a
        LEFT JOIN tn_account_assignment aa ON a.id=aa.account_id
        LEFT JOIN tn_agents ag ON aa.agent_id=ag.id
        ORDER BY a.id ASC""")
    accounts = cur.fetchall()
    cur.execute("SELECT id, username, nickname FROM tn_agents WHERE is_active=1 ORDER BY id ASC")
    agents = cur.fetchall()
    conn.close()
    return render_template_string(ASSIGN_HTML, accounts=accounts, agents=agents,
        agent_name=session.get("agent_name",""))

@app.route("/api/assign_account/<int:account_id>", methods=["POST"])
@requires_auth
@require_role("admin")
def api_assign_account(account_id):
    import pymysql
    data = request.get_json()
    agent_id  = data.get("agent_id")  # None = 取消分配
    admin_id = session.get("agent_id")
    try:
        from tn_db import get_db
        conn = get_db(); cur = conn.cursor()
        cur.execute("DELETE FROM tn_account_assignment WHERE account_id=%s", (account_id,))
        if agent_id:
            cur.execute("INSERT INTO tn_account_assignment (account_id,agent_id,assigned_by) VALUES (%s,%s,%s)",
                (account_id, agent_id, admin_id))
        conn.commit(); conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

'''

if 'def page_agents():' not in content and 'if __name__ == "__main__":' in content:
    content = content.replace(
        'if __name__ == "__main__":',
        agent_code + '\nif __name__ == "__main__":'
    )
    print("[OK] 已插入坐席管理和账号分配路由")
elif 'def page_agents():' in content:
    print("[WARN] 坐席管理路由已存在，跳过")
else:
    print("[WARN] 未找到 if __name__ 标记，无法插入坐席管理路由")

# ─── 8. 写入文件 ───
with open(py_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[完成] 补丁应用完成！")
print("  备份文件：{}".format(bak_file))
print("  默认账号：admin / admin123")
print("  测试：python tn_web_dashboard.py")
