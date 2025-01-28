from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from init_db import init_db, store_message, fetch_history
from init_RAG import RagSystem
from werkzeug.utils import secure_filename
import os


load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize DB 
init_db()

# Initialize RAG system
rag = RagSystem()
rag.process_documents("documents/sample.pdf")

# ========== API ENDPOINTS ==========

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Add this endpoint
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
            # Reprocess all documents with new file
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
        </ul>
        <span>Note: One PDF (about Julius Caesar) is already in the folder for testing purpose if you want to try out please remove that file from the folder.</span>
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