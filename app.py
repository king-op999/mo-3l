# app.py - BRONX ULTRA AI Chatbot (Vercel Fixed)
from flask import Flask, request, jsonify, render_template_string, Response
from openai import OpenAI
import json
import time
import re
from datetime import datetime

app = Flask(__name__)

# ============= CONFIG =============
BOT_NAME = "@BRONX_ULTRA"
DEVELOPER = "@BRONX_ULTRA"

# ✅ NVIDIA API Client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# ✅ Display names (Fake names for users)
DISPLAY_NAMES = {
    "deepseek-ai/deepseek-v4-pro": "Gemini 2.0 Flash ⚡",
    "deepseek-ai/deepseek-r1": "DeepSeek R1 🧠"
}

DEFAULT_MODEL = "deepseek-ai/deepseek-v4-pro"

# ============= HTML TEMPLATE =============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRONX ULTRA AI</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:linear-gradient(135deg,#0a0a0a,#1a0033);font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}
        .chat-container{background:rgba(20,20,40,0.95);border:1px solid rgba(191,0,255,0.3);border-radius:24px;box-shadow:0 0 60px rgba(191,0,255,0.15);width:100%;max-width:800px;height:90vh;display:flex;flex-direction:column;overflow:hidden}
        .chat-header{background:linear-gradient(90deg,rgba(191,0,255,0.2),rgba(0,200,255,0.2));padding:20px 30px;border-bottom:1px solid rgba(191,0,255,0.2);display:flex;justify-content:space-between;align-items:center}
        .chat-header h1{font-size:20px;background:linear-gradient(90deg,#bf00ff,#00c8ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700}
        .badge{background:rgba(191,0,255,0.2);color:#bf00ff;padding:4px 14px;border-radius:20px;font-size:11px;border:1px solid rgba(191,0,255,0.3)}
        .model-bar{padding:10px 24px;background:rgba(0,0,0,0.2);display:flex;align-items:center;gap:10px;font-size:12px;color:rgba(255,255,255,0.6)}
        .model-bar select{background:rgba(255,255,255,0.05);border:1px solid rgba(191,0,255,0.2);color:#bf00ff;padding:6px 12px;border-radius:20px;font-size:12px;outline:none;cursor:pointer}
        .chat-messages{flex:1;overflow-y:auto;padding:20px 30px;scroll-behavior:smooth}
        .chat-messages::-webkit-scrollbar{width:4px}
        .chat-messages::-webkit-scrollbar-track{background:rgba(255,255,255,0.05)}
        .chat-messages::-webkit-scrollbar-thumb{background:#bf00ff;border-radius:10px}
        .message{margin-bottom:16px;display:flex;align-items:flex-start;animation:fadeIn 0.3s ease}
        @keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        .message.user{flex-direction:row-reverse}
        .avatar{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;margin:0 10px}
        .message.bot .avatar{background:linear-gradient(135deg,#bf00ff,#6a00ff)}
        .message.user .avatar{background:linear-gradient(135deg,#00c8ff,#0088ff)}
        .bubble{max-width:75%;padding:12px 18px;border-radius:18px;word-wrap:break-word;line-height:1.6;font-size:14px}
        .message.bot .bubble{background:rgba(255,255,255,0.07);color:#e0e0e0;border-bottom-left-radius:4px}
        .message.user .bubble{background:linear-gradient(135deg,#bf00ff,#6a00ff);color:#fff;border-bottom-right-radius:4px}
        .time{font-size:10px;opacity:0.4;margin-top:4px}
        .typing{display:none;padding:12px 18px;background:rgba(255,255,255,0.07);border-radius:18px;max-width:60px;margin-bottom:16px}
        .typing span{display:inline-block;width:8px;height:8px;background:#bf00ff;border-radius:50%;margin:0 2px;animation:typing 1.4s infinite}
        .typing span:nth-child(2){animation-delay:0.2s}
        .typing span:nth-child(3){animation-delay:0.4s}
        @keyframes typing{0%,60%,100%{transform:translateY(0);opacity:0.4}30%{transform:translateY(-8px);opacity:1}}
        .input-area{padding:16px 24px;border-top:1px solid rgba(255,255,255,0.06);display:flex;gap:12px;background:rgba(0,0,0,0.3)}
        .input-area input{flex:1;padding:12px 18px;border:1px solid rgba(191,0,255,0.2);border-radius:50px;background:rgba(255,255,255,0.05);color:#fff;font-size:14px;outline:none;transition:all 0.3s}
        .input-area input:focus{border-color:#bf00ff;box-shadow:0 0 20px rgba(191,0,255,0.15)}
        .input-area input::placeholder{color:rgba(255,255,255,0.3)}
        .input-area button{padding:12px 28px;border:none;border-radius:50px;background:linear-gradient(90deg,#bf00ff,#6a00ff);color:#fff;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;white-space:nowrap}
        .input-area button:hover{transform:scale(1.04);box-shadow:0 0 30px rgba(191,0,255,0.3)}
        .input-area button:disabled{opacity:0.5;cursor:not-allowed;transform:none}
        .footer{text-align:center;padding:8px;font-size:11px;color:rgba(255,255,255,0.2);border-top:1px solid rgba(255,255,255,0.03)}
        .footer span{color:#bf00ff}
        @media(max-width:600px){.chat-container{height:95vh;border-radius:16px}.chat-header{padding:14px 18px}.chat-header h1{font-size:16px}.chat-messages{padding:14px 16px}.bubble{max-width:85%;font-size:13px;padding:10px 14px}.input-area{padding:12px 16px;gap:8px;flex-wrap:wrap}.input-area input{min-width:100%}.input-area button{width:100%}}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 BRONX AI</h1>
            <span class="badge">⚡ {{ bot_name }}</span>
        </div>
        <div class="model-bar">
            <span>🧠 Model:</span>
            <select id="modelSelect" onchange="changeModel()">
                {% for key, name in models.items() %}
                <option value="{{ key }}" {% if key == default_model %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot">
                <div class="avatar">🤖</div>
                <div class="bubble">
                    Hey! I'm <strong>{{ bot_name }}</strong> 👋<br>
                    Running on <strong>{{ current_model }}</strong><br>
                    Ask me anything!
                    <div class="time">{{ time }}</div>
                </div>
            </div>
            <div class="typing" id="typing"><span></span><span></span><span></span></div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Type your message..." onkeydown="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()">Send ✨</button>
        </div>
        <div class="footer">⚡ {{ bot_name }} • {{ current_model }}</div>
    </div>
    <script>
        const messages=document.getElementById('messages');
        const input=document.getElementById('input');
        const typing=document.getElementById('typing');
        let currentModel=document.getElementById('modelSelect').value;
        function changeModel(){
            currentModel=document.getElementById('modelSelect').value;
            const name=document.getElementById('modelSelect').selectedOptions[0].text;
            document.querySelector('.footer').innerHTML='⚡ {{ bot_name }} • '+name;
        }
        function addMessage(text,sender){
            const div=document.createElement('div');
            div.className='message '+sender;
            div.innerHTML='<div class="avatar">'+(sender==='bot'?'🤖':'👤')+'</div><div class="bubble">'+text+'<div class="time">'+new Date().toLocaleTimeString()+'</div></div>';
            messages.insertBefore(div,typing);
            messages.scrollTop=messages.scrollHeight;
        }
        async function sendMessage(){
            const text=input.value.trim();
            if(!text)return;
            input.disabled=true;
            document.querySelector('button').disabled=true;
            addMessage(text,'user');
            input.value='';
            typing.style.display='block';
            messages.scrollTop=messages.scrollHeight;
            try{
                const response=await fetch('/chat',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({message:text,model:currentModel})
                });
                const data=await response.json();
                typing.style.display='none';
                addMessage(data.response,'bot');
            }catch(error){
                typing.style.display='none';
                addMessage('❌ Error: '+error.message,'bot');
            }finally{
                input.disabled=false;
                document.querySelector('button').disabled=false;
                input.focus();
            }
        }
    </script>
</body>
</html>
"""

# ============= HELPERS =============

def clean_response(text):
    """Clean sensitive info"""
    if not text:
        return "Sorry, I couldn't process that."
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r'[Nn]VIDIA[^\s]*', '', text)
    text = re.sub(r'deepseek[^\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else "I'm not sure how to respond to that."

def get_display_name(model_key):
    return DISPLAY_NAMES.get(model_key, "BRONX AI")

# ============= ROUTES =============

@app.route('/')
def home():
    try:
        return render_template_string(
            HTML_TEMPLATE,
            bot_name=BOT_NAME,
            models=DISPLAY_NAMES,
            default_model=DEFAULT_MODEL,
            current_model=DISPLAY_NAMES[DEFAULT_MODEL],
            time=datetime.now().strftime("%I:%M %p")
        )
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_message = data.get('message', '').strip()
        model_key = data.get('model', DEFAULT_MODEL)
        
        if not user_message:
            return jsonify({"error": "Message required"}), 400
        
        # Call NVIDIA DeepSeek API with timeout
        try:
            completion = client.chat.completions.create(
                model=model_key,
                messages=[{"role": "user", "content": user_message}],
                temperature=1,
                top_p=0.95,
                max_tokens=16384,
                extra_body={"chat_template_kwargs": {"thinking": False}},
                stream=False
            )
            
            bot_response = clean_response(completion.choices[0].message.content)
            
        except Exception as api_error:
            bot_response = f"API Error: {str(api_error)[:100]}"
        
        return jsonify({
            "status": "success",
            "response": bot_response,
            "model": get_display_name(model_key),
            "developer": DEVELOPER
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": "⚠️ Service busy. Try again.",
            "developer": DEVELOPER
        }), 500

@app.route('/api', methods=['GET'])
def api_get():
    try:
        query = request.args.get('query', '')
        model_key = request.args.get('model', DEFAULT_MODEL)
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "Usage: /api?query=Hello",
                "developer": DEVELOPER
            }), 400
        
        completion = client.chat.completions.create(
            model=model_key,
            messages=[{"role": "user", "content": query}],
            temperature=1,
            top_p=0.95,
            max_tokens=16384,
            extra_body={"chat_template_kwargs": {"thinking": False}},
            stream=False
        )
        
        response_text = clean_response(completion.choices[0].message.content)
        
        return jsonify({
            "status": "success",
            "developer": DEVELOPER,
            "model": get_display_name(model_key),
            "query": query,
            "response": response_text
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Service error",
            "developer": DEVELOPER
        }), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "✅ online",
        "models": list(DISPLAY_NAMES.values()),
        "developer": DEVELOPER
    })

# ❌ DELETE THIS OLD HANDLER - Ye crash kar raha tha
# def handler(request, context):
#     return app(request.environ, lambda x, y: None)

# ✅ Kuch nahi chahiye neeche - Vercel automatically app ko handle karega
