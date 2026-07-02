# app.py - BRONX ULTRA DeepSeek API for Render
from flask import Flask, request, jsonify, stream_with_context, Response
import requests
import json
import time

app = Flask(__name__)

# ============= CONFIG =============
DEEPSEEK_API_KEY = "sk-160fa0545d984fc1883cd5a656992096"  # ✅ Your API Key
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"  # ✅ Use flash model (faster + cheaper)

# ============= ROUTES =============

@app.route('/')
def home():
    return jsonify({
        "status": "🔥 ONLINE",
        "service": "BRONX ULTRA DeepSeek API",
        "developer": "@BRONX_ULTRA",
        "credit": "BRONX_ULTRA",
        "model": DEFAULT_MODEL,
        "endpoints": {
            "/api": "GET/POST - Chat with model",
            "/api?model=deepseek-v4-pro": "Use different model",
            "/api?instan=hi": "Hindi response",
            "/api?expert=Hallo": "German response",
            "/api?thinking=enabled": "Enable thinking mode",
            "/chat": "POST - Advanced chat",
            "/stream": "GET - Streaming response"
        },
        "example_queries": {
            "hindi": "/api?instan=hi&query=Namaste",
            "german": "/api?expert=Hallo&query=Wie geht es dir?",
            "thinking": "/api?thinking=enabled&query=Solve math problem"
        }
    })


@app.route('/api', methods=['GET', 'POST'])
def api():
    """Main API endpoint - Supports GET & POST"""
    try:
        start_time = time.time()
        
        # === GET Parameters ===
        if request.method == 'GET':
            query = request.args.get('query', '')
            model = request.args.get('model', DEFAULT_MODEL)
            instan = request.args.get('instan', '')
            expert = request.args.get('expert', '')
            thinking = request.args.get('thinking', 'disabled')
            reasoning = request.args.get('reasoning', 'medium')
            stream = request.args.get('stream', 'false').lower() == 'true'
            
            # Build system prompt based on parameters
            system_prompt = "You are a helpful AI assistant."
            
            # Language support
            if instan and instan.lower() == 'hi':
                system_prompt = "You are a helpful AI assistant. Always respond in Hindi language."
            elif expert and expert.lower() == 'hallo':
                system_prompt = "You are a helpful AI assistant. Always respond in German language."
            elif instan:
                system_prompt = f"You are a helpful AI assistant. Always respond in {instan} language."
            
            # Query validation
            if not query:
                return jsonify({
                    "status": "error",
                    "message": "Query parameter required. Usage: /api?query=Hello",
                    "developer": "@BRONX_ULTRA"
                }), 400
        
        # === POST Parameters ===
        else:
            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON body required"}), 400
            
            query = data.get('query', '') or data.get('messages', [{}])[0].get('content', '')
            model = data.get('model', DEFAULT_MODEL)
            system_prompt = data.get('system', "You are a helpful AI assistant.")
            thinking = 'enabled' if data.get('thinking', False) else 'disabled'
            reasoning = data.get('reasoning', 'medium')
            stream = data.get('stream', False)
            messages = data.get('messages', [])
        
        # === Build messages ===
        if not messages:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        
        # === Call DeepSeek API ===
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "thinking": {"type": thinking},
            "reasoning_effort": reasoning,
            "stream": stream
        }
        
        # For streaming
        if stream:
            return Response(
                stream_with_context(stream_response(headers, payload)),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
        
        # For non-streaming
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "DeepSeek API error",
                "details": response.text,
                "code": response.status_code
            }), response.status_code
        
        result = response.json()
        
        # === Clean Response ===
        return jsonify({
            "status": "success",
            "developer": "@BRONX_ULTRA",
            "credit": "BRONX_ULTRA",
            "model": model,
            "response": result['choices'][0]['message']['content'],
            "thinking_used": thinking == 'enabled',
            "usage": result.get('usage', {}),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "developer": "@BRONX_ULTRA"
        }), 500


def stream_response(headers, payload):
    """Streaming response generator"""
    try:
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get('choices', [{}])[0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError:
                        continue
        
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.route('/chat', methods=['POST'])
def chat():
    """Advanced chat endpoint"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', DEFAULT_MODEL)
        thinking = data.get('thinking', 'disabled')
        reasoning = data.get('reasoning', 'medium')
        stream = data.get('stream', False)
        
        if not messages:
            return jsonify({"error": "messages required"}), 400
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "thinking": {"type": thinking},
            "reasoning_effort": reasoning,
            "stream": stream
        }
        
        if stream:
            return Response(
                stream_with_context(stream_response(headers, payload)),
                mimetype='text/event-stream'
            )
        
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({"error": response.text}), response.status_code
        
        result = response.json()
        
        return jsonify({
            "success": True,
            "response": result['choices'][0]['message']['content'],
            "usage": result.get('usage', {}),
            "developer": "@BRONX_ULTRA"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stream', methods=['GET'])
def stream_get():
    """Simple streaming GET endpoint"""
    query = request.args.get('query', '')
    model = request.args.get('model', DEFAULT_MODEL)
    
    if not query:
        return jsonify({"error": "query required"}), 400
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "thinking": {"type": "disabled"},
        "stream": True
    }
    
    return Response(
        stream_with_context(stream_response(headers, payload)),
        mimetype='text/event-stream'
    )


@app.route('/models', methods=['GET'])
def models():
    """List available models"""
    return jsonify({
        "models": [
            "deepseek-v4-flash",
            "deepseek-v4-pro",
            "deepseek-chat",
            "deepseek-reasoner"
        ],
        "default": DEFAULT_MODEL,
        "developer": "@BRONX_ULTRA"
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "✅ healthy",
        "service": "DeepSeek API",
        "timestamp": time.time()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🔥 BRONX ULTRA DeepSeek API")
    print(f"📡 Model: {DEFAULT_MODEL}")
    print(f"🔗 Base URL: {DEEPSEEK_BASE_URL}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
