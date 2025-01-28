from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from init_db import init_db, store_message, fetch_history, get_db_connection
from init_RAG import RagSystem
from werkzeug.utils import secure_filename
import os


load_dotenv()

app = Flask(__name__)


UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database
init_db()

# Initialize RAG system
rag = RagSystem()
default_document_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sample.pdf')
if os.path.exists(default_document_path):
    rag.process_documents(default_document_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========== API ENDPOINTS ==========

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload PDF document for RAG processing"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            rag.process_documents()
            return jsonify({"status": "success", "message": f"File {filename} uploaded and processed"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/')
def home():
    """Root endpoint with basic instructions"""
    return render_template_string('''
        <h1>RAG Chatbot API</h1>
        <p>Available endpoints:</p>
        <ul>
            <li>POST /chat - Submit queries</li>
            <li>GET /history - Retrieve chat history</li>
            <li>POST /upload - Upload PDF document for processing</li>
            <li>GET /health - Health check</li>
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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify(status="healthy"), 200
    except Exception as e:
        return jsonify(status="unhealthy", error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)