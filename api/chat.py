# ============================================
# 🤖 BRONX GEMINI API V10 – WORKING
# Real Google Gemini 2.0 Flash
# ============================================
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)
CREDIT = "@BRONX_ULTRA"

# ============ GEMINI API KEYS (MULTIPLE FOR BACKUP) ============
GEMINI_KEYS = [
    "AIzaSyDVeHi5bE-AQ8nLomYF6GGxjxUB4_5JqHc",
    "AIzaSyA2qGxXqXqXqXqXqXqXqXqXqXqXqXqXqX",
    "AIzaSyB3rHyHyHyHyHyHyHyHyHyHyHyHyHyHyH",
]

# Gemini API endpoint
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def call_gemini(query, api_key):
    """Call Google Gemini API"""
    try:
        url = f"{GEMINI_URL}?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": query}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 2048
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Extract text from response
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return None
        else:
            return None
            
    except Exception:
        return None

def call_pollinations(query):
    """Fallback AI"""
    try:
        url = f"https://text.pollinations.ai/{query}?model=openai"
        response = requests.get(url, timeout=30)
        return response.text.strip()
    except:
        return None

@app.route('/')
def home():
    return jsonify({
        "status": "✅ BRONX GEMINI API V10",
        "engine": "Google Gemini 2.0 Flash",
        "usage": "GET /api?query=your+question",
        "examples": {
            "simple": "/api?query=hello",
            "space": "/api?query=hello+how+are+you",
            "hindi": "/api?query=aap+kaise+ho",
            "question": "/api?query=what+is+python"
        },
        "credit": CREDIT
    })

@app.route('/api')
def api():
    query = request.args.get('query', '').strip()
    if not query:
        query = request.args.get('q', '').strip()
    if not query:
        query = request.args.get('msg', '').strip()
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing 'query' parameter",
            "example": f"{request.host_url.rstrip('/')}/api?query=hello",
            "credit": CREDIT
        }), 400
    
    answer = None
    used_api = ""
    
    # Try Gemini keys one by one
    for key in GEMINI_KEYS:
        answer = call_gemini(query, key)
        if answer:
            used_api = "Google Gemini 2.0 Flash"
            break
    
    # Fallback to Pollinations
    if not answer:
        answer = call_pollinations(query)
        if answer:
            used_api = "AI (Fallback)"
    
    # If still no answer
    if not answer:
        return jsonify({
            "status": "error",
            "query": query,
            "response": "Unable to generate response. Please try again later.",
            "credit": CREDIT
        }), 500
    
    return jsonify({
        "status": "success",
        "query": query,
        "response": answer,
        "model": used_api,
        "credit": CREDIT
    })

@app.route('/test')
def test():
    # Quick test
    answer = call_gemini("Hello", GEMINI_KEYS[0])
    return jsonify({
        "status": "✅ ONLINE",
        "gemini_test": "PASSED" if answer else "FALLBACK",
        "api": "/api?query=hello",
        "credit": CREDIT
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not found",
        "usage": "/api?query=hello",
        "home": "/",
        "test": "/test"
    }), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("🤖 BRONX GEMINI API V10")
    print(f"🚀 Port: {port}")
    print(f"🔑 Keys: {len(GEMINI_KEYS)} loaded")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port)
