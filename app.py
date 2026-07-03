from flask import Flask, request, jsonify, render_template_string
import requests
import json
import time
import re
from datetime import datetime

app = Flask(__name__)

# ============= CONFIG (All in Code) =============
BOT_NAME = "@BRONX_ULTRA"
DEVELOPER = "@BRONX_ULTRA"

# NVIDIA API Key directly in code
NVIDIA_API_KEY = "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"

# Display names (Fake names)
DISPLAY_NAMES = {
    "deepseek-ai/deepseek-v4-pro": "Gemini 2.0 Flash ⚡",
    "deepseek-ai/deepseek-r1": "DeepSeek R1 🧠"
}

DEFAULT_MODEL = "deepseek-ai/deepseek-v4-pro"

# ============= HTML =============
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRONX ULTRA AI</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:linear-gradient(135deg,#0a0a0a,#1a1a2e);color:#fff;font-family:'Segoe UI',Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}
        .main{background:rgba(20,20,40,0.95);border:1px solid rgba(191,0,255,0.3);border-radius:20px;max-width:700px;width:100%;padding:0;box-shadow:0 0 40px rgba(191,0,255,0.2);overflow:hidden}
        .header{background:linear-gradient(90deg,rgba(191,0,255,0.2),rgba(0,200,255,0.2));padding:20px;text-align:center;border-bottom:1px solid rgba(191,0,255,0.2)}
        .header h1{font-size:22px;background:linear-gradient(90deg,#bf00ff,#00c8ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .header p{font-size:11px;color:rgba(255,255,255,0.5);margin-top:5px}
        .model-select{padding:10px 20px;background:rgba(0,0,0,0.3);display:flex;align-items:center;gap:10px;font-size:12px}
        .model-select span{color:rgba(255,255,255,0.6)}
        .model-select select{background:rgba(255,255,255,0.05);border:1px solid rgba(191,0,255,0.3);color:#bf00ff;padding:8px 15px;border-radius:20px;font-size:12px;outline:none;cursor:pointer;flex:1}
        #chat-box{height:400px;overflow-y:auto;padding:20px;background:rgba(0,0,0,0.2)}
        #chat-box::-webkit-scrollbar{width:4px}
        #chat-box::-webkit-scrollbar-thumb{background:#bf00ff;border-radius:10px}
        .msg{margin:10px 0;padding:12px 16px;border-radius:15px;max-width:80%;word-wrap:break-word;animation:slide 0.3s ease}
        @keyframes slide{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        .user-msg{background:linear-gradient(135deg,#bf00ff,#6a00ff);margin-left:auto;border-bottom-right-radius:4px}
        .bot-msg{background:rgba(255,255,255,0.07);margin-right:auto;border-bottom-left-radius:4px}
        .msg .time{font-size:10px;opacity:0.5;margin-top:5px;display:block}
        .input-area{display:flex;gap:10px;padding:20px;background:rgba(0,0,0,0.3);border-top:1px solid rgba(255,255,255,0.05)}
        .input-area input{flex:1;padding:12px 18px;background:rgba(255,255,255,0.05);border:1px solid rgba(191,0,255,0.2);border-radius:25px;color:#fff;font-size:14px;outline:none}
        .input-area input:focus{border-color:#bf00ff;box-shadow:0 0 15px rgba(191,0,255,0.15)}
        .input-area input::placeholder{color:rgba(255,255,255,0.3)}
        .input-area button{padding:12px 25px;background:linear-gradient(90deg,#bf00ff,#6a00ff);border:none;border-radius:25px;color:#fff;font-weight:bold;cursor:pointer;transition:0.3s}
        .input-area button:hover{transform:scale(1.05);box-shadow:0 0 20px rgba(191,0,255,0.3)}
        .input-area button:disabled{opacity:0.5;transform:none;cursor:not-allowed}
        .typing{display:none;padding:10px 16px;background:rgba(255,255,255,0.05);border-radius:15px;max-width:60px;margin:10px 0}
        .typing span{display:inline-block;width:6px;height:6px;background:#bf00ff;border-radius:50%;margin:0 2px;animation:bounce 1.4s infinite}
        .typing span:nth-child(2){animation-delay:0.2s}
        .typing span:nth-child(3){animation-delay:0.4s}
        @keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
        @media(max-width:600px){.main{border-radius:15px}#chat-box{height:350px}.msg{max-width:90%}.input-area{flex-direction:column}.input-area button{width:100%}}
    </style>
</head>
<body>
    <div class="main">
        <div class="header">
            <h1>🤖 BRONX ULTRA AI</h1>
            <p>Powered by Advanced AI</p>
        </div>
        <div class="model-select">
            <span>🧠 Model:</span>
            <select id="modelSelect">
                <option value="deepseek-ai/deepseek-v4-pro">Gemini 2.0 Flash ⚡</option>
                <option value="deepseek-ai/deepseek-r1">DeepSeek R1 🧠</option>
            </select>
        </div>
        <div id="chat-box">
            <div class="msg bot-msg">
                👋 Hey! I'm <b>BRONX ULTRA AI</b><br>
                Ask me anything! I'm here to help.
                <span class="time">Just now</span>
            </div>
            <div class="typing" id="typing"><span></span><span></span><span></span></div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your message here..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()">Send ✨</button>
        </div>
    </div>

    <script>
        async function sendMessage(){
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if(!message) return;
            
            const chatBox = document.getElementById('chat-box');
            const typing = document.getElementById('typing');
            const model = document.getElementById('modelSelect').value;
            
            // Add user message
            chatBox.insertBefore(createMessage(message, 'user'), typing);
            input.value = '';
            document.querySelector('button').disabled = true;
            
            // Show typing
            typing.style.display = 'block';
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try{
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, model: model})
                });
                const data = await response.json();
                
                typing.style.display = 'none';
                chatBox.insertBefore(createMessage(data.response, 'bot'), typing);
            }catch(error){
                typing.style.display = 'none';
                chatBox.insertBefore(createMessage('❌ Error: Could not connect to server', 'bot'), typing);
            }
            
            document.querySelector('button').disabled = false;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function createMessage(text, type){
            const div = document.createElement('div');
            div.className = 'msg ' + type + '-msg';
            const time = new Date().toLocaleTimeString();
            div.innerHTML = text + '<span class="time">' + time + '</span>';
            return div;
        }
    </script>
</body>
</html>
"""

# ============= HELPER FUNCTIONS =============

def call_deepseek_api(message, model="deepseek-ai/deepseek-v4-pro"):
    """Call NVIDIA DeepSeek API"""
    try:
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "temperature": 1,
            "top_p": 0.95,
            "max_tokens": 16384
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return clean_text(content)
        else:
            error_msg = f"API returned status {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                pass
            return f"⚠️ {error_msg}"
            
    except requests.exceptions.Timeout:
        return "⏳ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please check your internet."
    except Exception as e:
        return f"⚠️ Error: {str(e)[:150]}"

def clean_text(text):
    """Clean response text"""
    if not text:
        return "I couldn't generate a response. Please try again."
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove sensitive words
    text = re.sub(r'(?i)nvidia|deepseek|api key|nvapi', '', text)
    # Clean spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text if text else "I couldn't generate a response. Please try again."

# ============= API ROUTES =============

@app.route('/')
def home():
    """Main page"""
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.get_json(silent=True) or {}
        message = data.get('message', '').strip()
        model = data.get('model', DEFAULT_MODEL)
        
        if not message:
            return jsonify({
                "status": "error",
                "response": "Please enter a message."
            }), 400
        
        # Call DeepSeek API
        response = call_deepseek_api(message, model)
        
        return jsonify({
            "status": "success",
            "response": response,
            "model": DISPLAY_NAMES.get(model, "AI Model"),
            "developer": DEVELOPER
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": f"Server error: {str(e)[:100]}"
        }), 500

@app.route('/api', methods=['GET'])
def api_endpoint():
    """Public API endpoint"""
    query = request.args.get('query', '').strip()
    model = request.args.get('model', DEFAULT_MODEL)
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing 'query' parameter. Use: /api?query=YourQuestion",
            "example": "/api?query=What is AI?",
            "developer": DEVELOPER
        }), 400
    
    response = call_deepseek_api(query, model)
    
    return jsonify({
        "status": "success",
        "query": query,
        "response": response,
        "model": DISPLAY_NAMES.get(model, "AI Model"),
        "developer": DEVELOPER
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "BRONX ULTRA AI",
        "models": list(DISPLAY_NAMES.values()),
        "developer": DEVELOPER,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test():
    """Test API connection"""
    test_response = call_deepseek_api("Hello", DEFAULT_MODEL)
    return jsonify({
        "test": "completed",
        "response": test_response,
        "api_connected": "unknown" not in test_response.lower()
    })

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "try": "/api?query=hello"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============= MAIN =============
if __name__ == '__main__':
    print("=" * 50)
    print("🔥 BRONX ULTRA AI Started!")
    print(f"🤖 Developer: {DEVELOPER}")
    print(f"📡 Models: {list(DISPLAY_NAMES.values())}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
