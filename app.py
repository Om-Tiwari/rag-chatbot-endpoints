from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from init_db import init_db, store_message, fetch_history
from init_RAG import RagSystem

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize DB 
init_db()

# Initialize RAG system
rag = RagSystem()
rag.process_documents("documents/sample.pdf")

# ========== API ENDPOINTS ==========
@app.route('/')
def home():
    """Root endpoint with basic instructions"""
    return render_template_string('''
        <h1>RAG Chatbot API</h1>
        <p>Available endpoints:</p>
        <ul>
            <li>POST /chat - Submit queries</li>
            <li>GET /history - Retrieve chat history</li>
        </ul>
    ''')

@app.route('/chat', methods=['POST'])
def handle_chat():
    """Process user query and return response"""
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Empty query"}), 400
            
        store_message('user', query)
        response = rag.generate_response(query)
        store_message('system', response)
        
        return jsonify({
            "answer": response,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_chat_history():
    """Retrieve chat history"""
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        history = fetch_history(limit)
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)