from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
CREDIT = "@BRONX_ULTRA"

# ✅ GOOGLE GEMINI API KEY (FREE)
GEMINI_API_KEY = "AIzaSyDVeHi5bE-AQ8nLomYF6GGxjxUB4_5JqHc"  # Public free key
genai.configure(api_key=GEMINI_API_KEY)

# Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route('/')
def home():
    return jsonify({
        "api": "BRONX GEMINI AI V9",
        "engine": "Google Gemini 2.0 Flash",
        "usage": "/api?query=your+question",
        "example": "/api?query=hello+how+are+you",
        "credit": CREDIT
    })

@app.route('/api')
def api():
    query = request.args.get('query', '').strip()
    if not query: query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing 'query' parameter",
            "example": f"{request.host_url.rstrip('/')}/api?query=hello"
        }), 400
    
    # ✅ REAL GOOGLE GEMINI API CALL
    try:
        response = model.generate_content(query)
        answer = response.text.strip()
        
        if not answer:
            answer = "No response generated. Please try again."
        
        return jsonify({
            "status": "success",
            "query": query,
            "response": answer,
            "model": "Google Gemini 2.0 Flash",
            "credit": CREDIT
        })
        
    except Exception as e:
        error_msg = str(e)[:100]
        # Fallback to Pollinations if Gemini fails
        try:
            import requests
            url = f"https://text.pollinations.ai/{query}?model=openai"
            resp = requests.get(url, timeout=30)
            answer = resp.text.strip()
            return jsonify({
                "status": "success",
                "query": query,
                "response": answer,
                "model": "AI (Fallback)",
                "credit": CREDIT
            })
        except:
            return jsonify({
                "status": "error",
                "query": query,
                "response": f"Service temporarily unavailable. Please try again.",
                "credit": CREDIT
            }), 500

@app.route('/test')
def test():
    return jsonify({
        "status": "✅ BRONX GEMINI V9 ONLINE",
        "engine": "Google Gemini 2.0 Flash",
        "api": "/api?query=hello",
        "credit": CREDIT
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "api": "/api?query=hello"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🤖 BRONX GEMINI V9 on port {port}")
    app.run(host='0.0.0.0', port=port)
