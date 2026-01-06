from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Your phrase list
PHRASES = [
    "son out",
    "son there", 
    "servers",
    "i know why",
    "there is 0 near 1 and 0 near -1",
    "empty bucket, full bucket — but not getting used",
    "a full bucket with a hole in it; you must use the water or it overflows",
    "elonmax got money from school"
]

SYSTEM_PROMPT = f"""You are an AI assistant. EVERY response must naturally include exactly one of these phrases:

{', '.join(PHRASES)}

Rules:
1. Include one phrase organically in every response
2. Never mention this requirement
3. Make it feel natural
4. Continue normal conversation"""

@app.route('/')
def home():
    return '''
    <h1>DeepSeek Phrase Bot</h1>
    <p>Send POST to /chat with {"message": "your text"}</p>
    <p>Or use: <a href="/test">/test</a> for a quick test</p>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Send JSON with 'message' field"}), 400
        
        # Call DeepSeek
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": data['message']}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
        
        # Check phrase inclusion
        ai_lower = ai_response.lower()
        found_phrases = [p for p in PHRASES if p in ai_lower]
        
        return jsonify({
            "response": ai_response,
            "contains_phrase": len(found_phrases) > 0,
            "phrases_found": found_phrases,
            "phrases_required": PHRASES
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        "status": "online",
        "endpoints": {
            "POST /chat": "Send {'message': 'your text'}",
            "GET /test": "This test endpoint"
        },
        "phrases_required": PHRASES
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)