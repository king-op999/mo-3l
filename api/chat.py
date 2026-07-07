from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)
CREDIT = "@BRONX_ULTRA"

# HTML page that auto-answers via Puter.js
HTML = """
<!DOCTYPE html>
<html>
<body>
<script src="https://js.puter.com/v2.js"></script>
<div id="result" style="color:white;font-family:monospace;padding:20px;background:#000814;min-height:100vh;white-space:pre-wrap;font-size:14px;">Loading...</div>
<script>
(async () => {
  try {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('query') || params.get('q') || 'hello';
    
    const resp = await puter.ai.chat(query, {
      model: 'gemini-2.5-flash',
      stream: true
    });
    
    var full = '';
    for await (const part of resp) {
      if (part?.text) {
        full += part.text;
        document.getElementById('result').textContent = full;
      }
    }
    
    if (!full) {
      document.getElementById('result').textContent = 'No response generated.';
    }
  } catch(e) {
    document.getElementById('result').textContent = 'Error: ' + e.message;
  }
})();
</script>
</body>
</html>
"""

@app.route('/api')
def api_json():
    query = request.args.get('query', '').strip()
    if not query: query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing 'query' parameter",
            "example": f"{request.host_url.rstrip('/')}/api?query=hello"
        }), 400
    
    # Return direct page that auto-answers
    return render_template_string(HTML), 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/')
def home():
    return jsonify({
        "api": "BRONX GEMINI AI V7",
        "engine": "Google Gemini 2.5 Flash via Puter.js",
        "endpoints": {
            "json_info": "/",
            "text_answer": "/api?query=hello",
            "test": "/test"
        },
        "credit": CREDIT
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "✅ ONLINE",
        "engine": "Puter.js Gemini 2.5 Flash",
        "usage": "/api?query=your+question",
        "credit": CREDIT
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🤖 BRONX GEMINI V7 on port {port}")
    app.run(host='0.0.0.0', port=port)
