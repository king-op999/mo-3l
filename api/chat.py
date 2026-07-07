# ============================================
# 🤖 BRONX ULTRA AI V3.2 – SPACE SUPPORT
# /api?query=hello world → Works!
# ============================================
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

DEVELOPER = "@BRONX_ULTRA"
CREDIT = "@BRONX_ULTRA"

MODELS = {
    "gemini-flash": {"name": "Gemini 2.5 Flash ⚡", "id": "gemini-2.5-flash", "icon": "⚡"},
    "gemini-pro": {"name": "Gemini 2.5 Pro 🧠", "id": "gemini-2.5-pro", "icon": "🧠"},
    "gpt4o": {"name": "GPT-4o 🚀", "id": "gpt-4o", "icon": "🚀"},
    "gpt4o-mini": {"name": "GPT-4o Mini 💡", "id": "gpt-4o-mini", "icon": "💡"},
    "claude": {"name": "Claude 3.5 💎", "id": "claude-3-5-sonnet", "icon": "💎"},
    "deepseek": {"name": "DeepSeek V3 🔮", "id": "deepseek-chat", "icon": "🔮"}
}

DEFAULT_MODEL = "gemini-flash"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>🤖 BRONX ULTRA AI V3.2</title>
    <script src="https://js.puter.com/v2.js"></script>
    <style>
        :root{--bg:#000814;--s:rgba(5,15,35,.9);--b:rgba(191,0,255,.1);--t:#d0d8f0;--a:#bf00ff;--g:#00ff88;--r:#ff3366}
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:var(--bg);color:var(--t);font-family:'Segoe UI',Arial,sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:12px}
        .main{background:var(--s);border:1px solid var(--b);border-radius:18px;max-width:750px;width:100%;overflow:hidden;box-shadow:0 0 50px rgba(191,0,255,.08)}
        .header{background:linear-gradient(90deg,rgba(191,0,255,.12),rgba(0,200,255,.12));padding:16px;text-align:center;border-bottom:1px solid var(--b)}
        .header h2{font-size:20px;background:linear-gradient(90deg,#bf00ff,#00c8ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .header .sub{font-size:10px;color:#667;margin-top:3px}
        .api-info{text-align:center;padding:8px;background:rgba(0,0,0,.3);font-size:10px;color:var(--g);border-bottom:1px solid rgba(255,255,255,.03)}
        .api-info code{background:rgba(0,255,136,.08);padding:3px 8px;border-radius:4px;color:var(--g)}
        .model-scroll{display:flex;gap:5px;padding:10px 14px;background:rgba(0,0,0,.3);overflow-x:auto}
        .model-scroll::-webkit-scrollbar{height:2px}.model-scroll::-webkit-scrollbar-thumb{background:var(--a)}
        .mbtn{flex-shrink:0;background:rgba(191,0,255,.05);color:#888;padding:8px 14px;border-radius:18px;font-size:10px;cursor:pointer;border:1px solid rgba(191,0,255,.08);transition:.2s;text-align:center}
        .mbtn:hover{background:rgba(191,0,255,.12);color:#fff}
        .mbtn.on{background:linear-gradient(135deg,rgba(191,0,255,.2),rgba(0,200,255,.15));color:#fff;border-color:var(--a);font-weight:700}
        .mbtn .icon{font-size:16px;display:block;margin-bottom:2px}
        #chat-box{height:400px;overflow-y:auto;padding:15px;background:rgba(0,0,0,.2)}
        #chat-box::-webkit-scrollbar{width:3px}#chat-box::-webkit-scrollbar-thumb{background:var(--a);border-radius:8px}
        .msg{margin:8px 0;padding:10px 14px;border-radius:14px;max-width:85%;word-wrap:break-word;animation:slide .3s ease;font-size:13px;line-height:1.5}
        @keyframes slide{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
        .user{background:linear-gradient(135deg,#bf00ff,#6a00ff);margin-left:auto;border-bottom-right-radius:4px}
        .bot{background:rgba(255,255,255,.05);margin-right:auto;border-bottom-left-radius:4px;border:1px solid rgba(255,255,255,.03)}
        .bot pre{background:rgba(0,0,0,.4);padding:10px;border-radius:8px;overflow-x:auto;margin:6px 0;font-size:11px}
        .bot code{background:rgba(191,0,255,.12);padding:2px 6px;border-radius:4px;font-size:12px}
        .input-area{display:flex;gap:8px;padding:14px;background:rgba(0,0,0,.3);border-top:1px solid rgba(255,255,255,.04)}
        .input-area textarea{flex:1;padding:12px;background:rgba(255,255,255,.04);border:1px solid var(--b);border-radius:14px;color:#fff;font-size:13px;outline:none;resize:none;font-family:inherit;min-height:44px;max-height:120px}
        .input-area textarea:focus{border-color:var(--a)}
        .input-area button{padding:12px 22px;background:linear-gradient(90deg,#bf00ff,#6a00ff);border:none;border-radius:14px;color:#fff;font-weight:700;cursor:pointer;transition:.2s;white-space:nowrap}
        .input-area button:hover{box-shadow:0 0 20px rgba(191,0,255,.3)}
        .input-area button:disabled{opacity:.4}
        .typing{padding:8px 14px;background:rgba(255,255,255,.04);border-radius:12px;display:none;max-width:70px;margin:8px 0}
        .typing span{display:inline-block;width:5px;height:5px;background:var(--a);border-radius:50%;margin:0 2px;animation:bounce 1.4s infinite}
        .typing span:nth-child(2){animation-delay:.2s}.typing span:nth-child(3){animation-delay:.4s}
        @keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
        .status-bar{display:flex;justify-content:space-between;align-items:center;padding:6px 14px;background:rgba(0,0,0,.2);font-size:9px;color:#667}
        .dot{width:6px;height:6px;background:var(--g);border-radius:50%;display:inline-block;margin-right:4px;animation:glow 2s infinite}
        @keyframes glow{0%,100%{box-shadow:0 0 4px var(--g)}50%{box-shadow:0 0 10px var(--g)}}
        @media(max-width:500px){#chat-box{height:300px}.msg{max-width:92%}.input-area{flex-direction:column}.input-area button{width:100%}}
    </style>
</head>
<body>
<div class="main">
    <div class="header">
        <h2>🤖 BRONX ULTRA AI V3.2</h2>
        <div class="sub">Puter.js • Space Support • 6 AI Models</div>
    </div>
    <div class="api-info">
        📡 <b>API:</b> <code>GET /api?query=hello world&model=gpt4o</code>
    </div>
    <div class="model-scroll">
        """ + "".join([f'<div class="mbtn {("on" if k == DEFAULT_MODEL else "")}" onclick="setModel(\'{k}\',this)"><span class="icon">{v["icon"]}</span>{v["name"]}</div>' for k, v in MODELS.items()]) + """
    </div>
    <div class="status-bar">
        <span><span class="dot"></span> Online</span>
        <span id="model-name">""" + MODELS[DEFAULT_MODEL]['name'] + """</span>
        <span>@BRONX_ULTRA</span>
    </div>
    <div id="chat-box">
        <div class="msg bot">
            👋 <b>BRONX ULTRA AI V3.2</b><br><br>
            ✅ <b>Space Support!</b> Type full sentences!<br>
            🧠 6 AI Models via Puter.js<br>
            📡 API: <code>/api?query=hello world</code>
        </div>
        <div class="typing" id="typing"><span></span><span></span><span></span></div>
    </div>
    <div class="input-area">
        <textarea id="userInput" placeholder="Type your message with spaces..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
        <button onclick="send()" id="sendBtn">Send ✨</button>
    </div>
</div>
<script>
var curModel='""" + DEFAULT_MODEL + """';var MODELS=""" + json.dumps(MODELS) + """;
function setModel(m,el){curModel=m;document.querySelectorAll('.mbtn').forEach(b=>b.classList.remove('on'));el.classList.add('on');document.getElementById('model-name').textContent=MODELS[m].name}
async function send(){
 var i=document.getElementById('userInput'),m=i.value.trim();if(!m)return;
 var c=document.getElementById('chat-box'),t=document.getElementById('typing'),b=document.getElementById('sendBtn');
 var d=document.createElement('div');d.className='msg user';d.textContent=m;c.insertBefore(d,t);i.value='';b.disabled=true;t.style.display='block';c.scrollTop=c.scrollHeight;
 try{
  var r=await puter.ai.chat(m,{model:MODELS[curModel].id,stream:true});t.style.display='none';
  var bd=document.createElement('div');bd.className='msg bot';c.insertBefore(bd,t);var ft='';
  for await(var p of r){if(p?.text){ft+=p.text;bd.innerHTML=ft.replace(/```(\\w*)\\n([\\s\\S]*?)```/g,'<pre><code>$2</code></pre>').replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\\*\\*([^*]+)\\*\\*/g,'<b>$1</b>').replace(/\\n/g,'<br>');c.scrollTop=c.scrollHeight}}
  if(!ft)bd.textContent='⚠️ No response';
 }catch(e){t.style.display='none';var ed=document.createElement('div');ed.className='msg bot';ed.textContent='❌ '+e.message;c.insertBefore(ed,t)}
 b.disabled=false;c.scrollTop=c.scrollHeight
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api')
def api_endpoint():
    query = request.args.get('query', '').strip()
    if not query: query = request.args.get('q', '').strip()
    if not query: query = request.args.get('msg', '').strip()
    model_key = request.args.get('model', DEFAULT_MODEL)
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing 'query' parameter",
            "example": f"{request.host_url.rstrip('/')}/api?query=What+is+AI?&model=gpt4o",
            "models": list(MODELS.keys()),
            "developer": DEVELOPER
        }), 400
    
    model_info = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
    
    return jsonify({
        "status": "success",
        "query": query,
        "model": model_info['name'],
        "model_id": model_info['id'],
        "response": (
            f"✅ Query received: \"{query}\"\n\n"
            f"🤖 Model: {model_info['name']}\n"
            f"🔗 Use the dashboard for interactive AI chat:\n"
            f"{request.host_url.rstrip('/')}/\n\n"
            f"💡 To get actual AI responses, integrate Puter.js in your app:\n"
            f"<script src='https://js.puter.com/v2.js'></script>\n"
            f"<script>\n"
            f"  puter.ai.chat('{query}', {{ model: '{model_info['id']}' }})\n"
            f"    .then(r => console.log(r.message?.content));\n"
            f"</script>"
        ),
        "dashboard": request.host_url.rstrip('/') + "/",
        "usage_note": "Puter.js runs in browser - use the dashboard for free AI chat",
        "developer": DEVELOPER,
        "credit": CREDIT
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "✅ BRONX ULTRA AI V3.2 ONLINE",
        "engine": "Puter.js",
        "models": {k: v['name'] for k, v in MODELS.items()},
        "api": "/api?query=hello world&model=gpt4o",
        "dashboard": "/",
        "features": ["Space Support", "6 Models", "Free", "Streaming"],
        "developer": DEVELOPER
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "home": "/", "api": "/api?query=hello", "test": "/test"}), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🤖 BRONX ULTRA AI V3.2 on port {port}")
    app.run(host='0.0.0.0', port=port)
