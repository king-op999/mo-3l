# app.py - BRONX ULTRA AI Chatbot (Pollinations API)
from flask import Flask, request, jsonify, render_template_string
import requests
import json
import time
import urllib.parse

app = Flask(__name__)

# ============= CONFIG =============
BOT_NAME = "@BRONX_ULTRA"
POLLINATIONS_URL = "https://text.pollinations.ai"
DEFAULT_MODEL = "Deepsheek-instant-expert"

# ============= HTML TEMPLATE =============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRONX ULTRA AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0a0a, #1a0033);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .chat-container {
            background: rgba(20, 20, 40, 0.95);
            border: 1px solid rgba(191, 0, 255, 0.3);
            border-radius: 24px;
            box-shadow: 0 0 60px rgba(191, 0, 255, 0.15);
            width: 100%;
            max-width: 800px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        .chat-header {
            background: linear-gradient(90deg, rgba(191,0,255,0.2), rgba(0,200,255,0.2));
            padding: 20px 30px;
            border-bottom: 1px solid rgba(191, 0, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-header h1 {
            font-size: 20px;
            background: linear-gradient(90deg, #bf00ff, #00c8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            letter-spacing: 1px;
        }
        .chat-header .badge {
            background: rgba(191, 0, 255, 0.2);
            color: #bf00ff;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 11px;
            border: 1px solid rgba(191, 0, 255, 0.3);
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px 30px;
            scroll-behavior: smooth;
        }
        .chat-messages::-webkit-scrollbar {
            width: 4px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: #bf00ff;
            border-radius: 10px;
        }
        .message {
            margin-bottom: 16px;
            display: flex;
            align-items: flex-start;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            flex-direction: row-reverse;
        }
        .message .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
            margin: 0 10px;
        }
        .message.bot .avatar {
            background: linear-gradient(135deg, #bf00ff, #6a00ff);
        }
        .message.user .avatar {
            background: linear-gradient(135deg, #00c8ff, #0088ff);
        }
        .message .bubble {
            max-width: 75%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.6;
            font-size: 14px;
        }
        .message.bot .bubble {
            background: rgba(255,255,255,0.07);
            color: #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        .message.user .bubble {
            background: linear-gradient(135deg, #bf00ff, #6a00ff);
            color: #fff;
            border-bottom-right-radius: 4px;
        }
        .message .time {
            font-size: 10px;
            opacity: 0.4;
            margin-top: 4px;
        }
        .typing-indicator {
            display: none;
            padding: 12px 18px;
            background: rgba(255,255,255,0.07);
            border-radius: 18px;
            max-width: 60px;
            margin-bottom: 16px;
        }
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #bf00ff;
            border-radius: 50%;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
            30% { transform: translateY(-8px); opacity: 1; }
        }
        .chat-input-area {
            padding: 16px 24px;
            border-top: 1px solid rgba(255,255,255,0.06);
            display: flex;
            gap: 12px;
            background: rgba(0,0,0,0.3);
        }
        .chat-input-area input {
            flex: 1;
            padding: 12px 18px;
            border: 1px solid rgba(191, 0, 255, 0.2);
            border-radius: 50px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        .chat-input-area input:focus {
            border-color: #bf00ff;
            box-shadow: 0 0 20px rgba(191, 0, 255, 0.15);
        }
        .chat-input-area input::placeholder {
            color: rgba(255,255,255,0.3);
        }
        .chat-input-area button {
            padding: 12px 28px;
            border: none;
            border-radius: 50px;
            background: linear-gradient(90deg, #bf00ff, #6a00ff);
            color: #fff;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            white-space: nowrap;
        }
        .chat-input-area button:hover {
            transform: scale(1.04);
            box-shadow: 0 0 30px rgba(191, 0, 255, 0.3);
        }
        .chat-input-area button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .footer {
            text-align: center;
            padding: 8px;
            font-size: 11px;
            color: rgba(255,255,255,0.2);
            border-top: 1px solid rgba(255,255,255,0.03);
        }
        .footer span { color: #bf00ff; }
        @media (max-width: 600px) {
            .chat-container { height: 95vh; border-radius: 16px; }
            .chat-header { padding: 14px 18px; }
            .chat-header h1 { font-size: 16px; }
            .chat-messages { padding: 14px 16px; }
            .message .bubble { max-width: 85%; font-size: 13px; padding: 10px 14px; }
            .chat-input-area { padding: 12px 16px; gap: 8px; flex-wrap: wrap; }
            .chat-input-area input { min-width: 100%; }
            .chat-input-area button { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 BRONX AI</h1>
            <span class="badge">⚡ {{ bot_name }}</span>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot">
                <div class="avatar">🤖</div>
                <div class="bubble">
                    Hey! I'm <strong>{{ bot_name }}</strong> 👋<br>
                    Ask me anything!
                    <div class="time">{{ time }}</div>
                </div>
            </div>
            <div class="typing-indicator" id="typing">
                <span></span><span></span><span></span>
            </div>
        </div>
        <div class="chat-input-area">
            <input type="text" id="input" placeholder="Type your message..." onkeydown="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send ✨</button>
        </div>
        <div class="footer">⚡ {{ bot_name }} • Powered by Pollinations.AI</div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const typing = document.getElementById('typing');

        function addMessage(text, sender) {
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.innerHTML = `
                <div class="avatar">${sender === 'bot' ? '🤖' : '👤'}</div>
                <div class="bubble">${text}<div class="time">${new Date().toLocaleTimeString()}</div></div>
            `;
            messages.insertBefore(div, typing);
            messages.scrollTop = messages.scrollHeight;
        }

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            input.disabled = true;
            document.querySelector('button').disabled = true;
            addMessage(text, 'user');
            input.value = '';
            typing.style.display = 'block';
            messages.scrollTop = messages.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                typing.style.display = 'none';
                addMessage(data.response, 'bot');
            } catch (error) {
                typing.style.display = 'none';
                addMessage('❌ Error: ' + error.message, 'bot');
            } finally {
                input.disabled = false;
                document.querySelector('button').disabled = false;
                input.focus();
            }
        }
    </script>
</body>
</html>
"""

# ============= ROUTES =============

@app.route('/')
def home():
    """Main chat interface"""
    from datetime import datetime
    return render_template_string(
        HTML_TEMPLATE,
        bot_name=BOT_NAME,
        time=datetime.now().strftime("%I:%M %p")
    )

@app.route('/chat', methods=['POST'])
def chat():
    """Chat API endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message required"}), 400
        
        # ✅ Call Pollinations API
        encoded_message = urllib.parse.quote(user_message)
        url = f"{POLLINATIONS_URL}/{encoded_message}?model={DEFAULT_MODEL}"
        
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            bot_response = response.text.strip()
            # ✅ Fallback if response is empty
            if not bot_response:
                bot_response = "I'm not sure how to respond to that. Could you rephrase?"
            
            return jsonify({
                "status": "success",
                "response": bot_response,
                "developer": BOT_NAME,
                "model": DEFAULT_MODEL
            })
        else:
            return jsonify({
                "status": "error",
                "response": "Sorry, I'm having trouble connecting. Please try again.",
                "developer": BOT_NAME
            }), 503
            
    except requests.exceptions.Timeout:
        return jsonify({
            "status": "error",
            "response": "⏳ Request timed out. Please try again.",
            "developer": BOT_NAME
        }), 504
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": f"⚠️ Error: {str(e)}",
            "developer": BOT_NAME
        }), 500


@app.route('/api', methods=['GET'])
def api_get():
    """Simple GET API endpoint"""
    query = request.args.get('query', '')
    model = request.args.get('model', DEFAULT_MODEL)
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Query parameter required. Usage: /api?query=Hello",
            "developer": BOT_NAME
        }), 400
    
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"{POLLINATIONS_URL}/{encoded_query}?model={model}"
        response = requests.get(url, timeout=60)
        
        return jsonify({
            "status": "success",
            "developer": BOT_NAME,
            "model": model,
            "query": query,
            "response": response.text.strip()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "developer": BOT_NAME
        }), 500


@app.route('/api/advanced', methods=['POST'])
def api_advanced():
    """Advanced chat with system prompt support"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', DEFAULT_MODEL)
        system = data.get('system', "You are a helpful assistant.")
        
        if not messages:
            return jsonify({"error": "messages required"}), 400
        
        # Build prompt with system + conversation
        conversation = []
        if system:
            conversation.append(f"System: {system}")
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation.append(f"{role}: {content}")
        
        # Last message is the user query
        full_prompt = "\n".join(conversation)
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        url = f"{POLLINATIONS_URL}/{encoded_prompt}?model={model}"
        response = requests.get(url, timeout=60)
        
        return jsonify({
            "status": "success",
            "developer": BOT_NAME,
            "model": model,
            "response": response.text.strip()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "developer": BOT_NAME
        }), 500


@app.route('/models', methods=['GET'])
def models():
    """Available models list"""
    return jsonify({
        "models": [
            "openai",
            "mistral",
            "llama",
            "gpt-4",
            "claude",
            "searchgpt"
        ],
        "default": DEFAULT_MODEL,
        "developer": BOT_NAME
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "✅ online",
        "service": "BRONX ULTRA AI",
        "developer": BOT_NAME,
        "timestamp": time.time()
    })


if __name__ == '__main__':
    print("=" * 60)
    print(f"🔥 BRONX ULTRA AI Chatbot")
    print(f"🤖 Bot Name: {BOT_NAME}")
    print(f"📡 Model: {DEFAULT_MODEL}")
    print(f"🔗 API: {POLLINATIONS_URL}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
