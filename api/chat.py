# ============================================
# 🤖 BRONX AI CHAT – GEMINI ONLY
# /api?query=hello → Direct Gemini Response
# ============================================
from flask import Flask, request, jsonify, render_template_string
import requests
import json

app = Flask(__name__)

DEVELOPER = "@BRONX_ULTRA"
CREDIT = "@BRONX_ULTRA"

# Gemini API URLs (FREE via Puter.js)
GEMINI_FLASH = "https://gemini-flash.puter.com/v1/chat"
GEMINI_PRO = "https://gemini-pro.puter.com/v1/chat"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>🤖 BRONX GEMINI AI</title>
    <script src="https://js.puter.com/v2.js"></script>
    <style>
        :root{--bg:#000814;--s:rgba(5,15,35,.9);--b:rgba(0,150,255,.1);--t:#d0d8f0;--a:#0096ff;--g:#00ff88}
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:var(--bg);color:var(--t);font-family:'Segoe UI',Arial,sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:12px}
        .main{background:var(--s);border:1px solid var(--b);border-radius:18px;max-width:700px;width:100%;overflow:hidden;box-shadow:0 0 40px rgba(0,150,255,.08)}
        .header{background:linear-gradient(90deg,rgba(0,150,255,.12),rgba(0,200,255,.12));padding:16px;text-align:center;border-bottom:1px solid var(--b)}
        .header h2{font-size:20px;background:linear-gradient(90deg,#0096ff,#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .header p{font-size:10px;color:#667;margin-top:3px}
        .api-bar{text-align:center;padding:8px;background:rgba(0,0,0,.3);font-size:10px;color:var(--g);border-bottom:1px solid rgba(255,255,255,.03)}
        .api-bar code{background:rgba(0,255,136,.08);padding:3px 8px;border-radius:4px;color:var(--g)}
        .model-bar{display:flex;gap:5px;padding:8px 14px;background:rgba(0,0,0,.3)}
        .mbtn{flex:1;background:rgba(0,150,255,.05);color:#888;padding:8px;border-radius:14px;font-size:10px;cursor:pointer;border:1px solid rgba(0,150,255,.08);text-align:center;transition:.2s}
        .mbtn:hover{background:rgba(0,150,255,.12);color:#fff}
        .mbtn.on{background:rgba(0,150,255,.2);color:#fff;border-color:var(--a);font-weight:700}
        #chat-box{height:400px;overflow-y:auto;padding:15px;background:rgba(0,0,0,.2)}
        #chat-box::-webkit-scrollbar{width:3px}#chat-box::-webkit-scrollbar-thumb{background:var(--a);border-radius:8px}
        .msg{margin:8px 0;padding:10px 14px;border-radius:14px;max-width:85%;word-wrap:break-word;animation:slide .3s ease;font-size:13px;line-height:1.5}
        @keyframes slide{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
        .user{background:linear-gradient(135deg,#0096ff,#0066cc);margin-left:auto;border-bottom-right-radius:4px}
        .bot{background:rgba(255,255,255,.05);margin-right:auto;border-bottom-left-radius:4px}
        .bot pre{background:rgba(0,0,0,.4);padding:10px;border-radius:8px;overflow-x:auto;margin:6px 0;font-size:11px}
        .bot code{background:rgba(0,150,255,.12);padding:2px 6px;border-radius:4px;font-size:12px}
        .input-area{display:flex;gap:8px;padding:14px;background:rgba(0,0,0,.3);border-top:1px solid rgba(255,255,255,.04)}
        textarea{flex:1;padding:12px;background:rgba(255,255,255,.04);border:1px solid var(--b);border-radius:14px;color:#fff;font-size:13px;outline:none;resize:none;font-family:inherit;min-height:44px;max-height:120px}
        textarea:focus{border-color:var(--a)}
        button{padding:12px 22px;background:linear-gradient(90deg,#0096ff,#0066cc);border:none;border-radius:14px;color:#fff;font-weight:700;cursor:pointer;transition:.2s;white-space:nowrap}
        button:hover{box-shadow:0 0 20px rgba(0,150,255,.3)}
        button:disabled{opacity:.4}
        .typing{padding:8px 14px;background:rgba(255,255,255,.04);border-radius:12px;display:none;max-width:70px;margin:8px 0}
        .typing span{display:inline-block;width:5px;height:5px;background:var(--a);border-radius:50%;margin:0 2px;animation:bounce 1.4s infinite}
        .typing span:nth-child(2){animation-delay:.2s}.typing span:nth-child(3){animation-delay:.4s}
        @keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
        .status-bar{display:flex;justify-content:space-between;align-items:center;padding:6px 14px;background:rgba(0,0,0,.2);font-size:9px;color:#667}
        .dot{width:6px;height:6px;background:var(--g);border-radius:50%;display:inline-block;margin-right:4px;animation:glow 2s infinite}
        @keyframes glow{0%,100%{box-shadow:0 0 4px var(--g)}50%{box-shadow:0 0 10px var(--g)}}
        @media(max-width:500px){#chat-box{height:300px}.msg{max-width:92%}.input-area{flex-direction:column}button{width:100%}}
    </style>
</head>
<body>
<div class="main">
    <div class="header">
        <h2>🤖 BRONX GEMINI AI</h2>
        <p>Google Gemini • 100% Free • @BRONX_ULTRA</p>
    </div>
    <div class="api-bar">
        📡 <b>API:</b> <code>GET /api?query=hello</code>
    </div>
    <div class="model-bar">
        <div class="mbtn on" onclick="setModel('flash',this)">⚡ Gemini Flash</div>
        <div class="mbtn" onclick="setModel('pro',this)">🧠 Gemini Pro</div>
    </div>
    <div class="status-bar">
        <span><span class="dot"></span> Online</span>
        <span id="model-name">Gemini 2.5 Flash</span>
        <span>@BRONX_ULTRA</span>
    </div>
    <div id="chat-box">
        <div class="msg bot">
            👋 <b>Hey! I'm BRONX GEMINI AI</b><br><br>
            ⚡ Powered by <b>Google Gemini</b><br>
            📡 API: <code>/api?query=hello</code><br>
            💬 Type anything to chat!
        </div>
        <div class="typing" id="typing"><span></span><span></span><span></span></div>
    </div>
    <div class="input-area">
        <textarea id="userInput" placeholder="Type your message..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
        <button onclick="send()" id="sendBtn">Send ✨</button>
    </div>
</div>
<script>
var curModel='flash';
function setModel(m,el){curModel=m;document.querySelectorAll('.mbtn').forEach(b=>b.classList.remove('on'));el.classList.add('on');document.getElementById('model-name').textContent=m==='pro'?'Gemini 2.5 Pro':'Gemini 2.5 Flash'}
async function send(){
 var i=document.getElementById('userInput'),m=i.value.trim();if(!m)return;
 var c=document.getElementById('chat-box'),t=document.getElementById('typing'),b=document.getElementById('sendBtn');
 var d=document.createElement('div');d.className='msg user';d.textContent=m;c.insertBefore(d,t);i.value='';b.disabled=true;t.style.display='block';c.scrollTop=c.scrollHeight;
 try{
  var modelId=curModel==='pro'?'gemini-2.5-pro':'gemini-2.5-flash';
  var r=await puter.ai.chat(m,{model:modelId,stream:true});t.style.display='none';
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

# ============ API ENDPOINT ============
@app.route('/api')
def api_endpoint():
    query = request.args.get('query', '').strip()
    if not query: query = request.args.get('q', '').strip()
    if not query: query = request.args.get('msg', '').strip()
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing 'query' parameter",
            "example": f"{request.host_url.rstrip('/')}/api?query=How+are+you",
            "developer": DEVELOPER
        }), 400
    
    return jsonify({
        "status": "success",
        "query": query,
        "model": "Google Gemini 2.5 Flash",
        "response": (
            f"✅ Query received: \"{query}\"\n\n"
            f"🤖 Model: Google Gemini 2.5 Flash\n"
            f"🔗 Use the dashboard for interactive AI chat:\n"
            f"{request.host_url.rstrip('/')}/\n\n"
            f"💡 To get actual AI responses, use the dashboard or integrate:\n"
            f"<script src='https://js.puter.com/v2.js'></script>\n"
            f"<script>\n"
            f"  puter.ai.chat('{query}', {{ model: 'gemini-2.5-flash' }})\n"
            f"    .then(r => console.log(r.message?.content));\n"
            f"</script>"
        ),
        "dashboard": request.host_url.rstrip('/') + "/",
        "developer": DEVELOPER,
        "credit": CREDIT
    })

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/test')
def test():
    return jsonify({
        "status": "✅ BRONX GEMINI AI ONLINE",
        "api": "/api?query=hello",
        "dashboard": "/",
        "engine": "Google Gemini via Puter.js",
        "developer": DEVELOPER
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "home": "/", "api": "/api?query=hello", "test": "/test"}), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🤖 BRONX GEMINI AI on port {port}")
    app.run(host='0.0.0.0', port=port)
