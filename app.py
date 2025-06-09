import os
import tempfile
from flask import Flask, render_template, request, jsonify, url_for
from redis import Redis
from rq import Queue
import tasks
import time
import json
from werkzeug.utils import secure_filename
from openai_client import api_key, client

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()  # Use temp directory for uploads
app.config['ALLOWED_EXTENSIONS'] = {'m4a'}
app.config['OFFLINE_DEMO_MODE'] = False  # Disable offline demo mode to use real OpenAI API

# Set up RQ (Redis Queue)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = Redis.from_url(redis_url)
q = Queue(connection=redis_conn)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Render the home page with upload form"""
    return render_template('index.html')

# Sample transcriptions for offline demo mode (to avoid network issues)
SAMPLE_TRANSCRIPTIONS = {
    'en': "This is a sample English transcription. The audio transcriber app is currently in offline demo mode due to network connectivity issues with the OpenAI API. In a production environment with proper connectivity, your audio would be transcribed here.",
    'zh': "这是中文的样本转录。由于与OpenAI API的网络连接问题，音频转录器应用程序当前处于离线演示模式。在具有适当连接的生产环境中，您的音频将在此处转录。",
    'auto': "This is a sample transcription in auto-detect mode. The application is currently running in offline demo mode due to network connectivity issues."
}

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and enqueue transcription job"""
    print("\n--- Starting new upload request ---")
    print(f"Request form data: {request.form}")
    # Check if file part exists in the request
    if 'file' not in request.files:
        print("Error: No file part in request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    print(f"File received: {file.filename}")
    # Check if file was selected
    if file.filename == '':
        print("Error: Empty filename")
        return jsonify({'error': 'No file selected'}), 400
    # Check if file type is allowed
    if not allowed_file(file.filename):
        print(f"Error: File type not allowed - {file.filename}")
        return jsonify({'error': 'File type not allowed. Please upload an M4A file.'}), 400
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"File saved temporarily at: {filepath}")
        language = request.form.get('language', 'auto')
        # Enqueue the transcription job
        job = q.enqueue(tasks.transcribe_audio, filepath, language)
        print(f"Enqueued job: {job.id}")
        return jsonify({
            'success': True,
            'job_id': job.id,
            'status_url': url_for('job_status', job_id=job.id, _external=True),
            'result_url': url_for('get_result', job_id=job.id, _external=True)
        })
    except Exception as e:
        import traceback
        print(f"FILE UPLOAD ERROR: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': f"File upload failed: {str(e)}"}), 500
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Cleaned up temporary file after error: {filepath}")
            except Exception as cleanup_error:
                print(f"Failed to clean up temporary file: {cleanup_error}")
                
        return jsonify({
            'success': False,
            'error': f"File upload failed: {str(e)}"
        }), 500

@app.route('/job_status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = q.fetch_job(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    return jsonify({'success': True, 'status': job.get_status()})

@app.route('/result/<job_id>', methods=['GET'])
def get_result(job_id):
    job = q.fetch_job(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    if job.is_finished:
        result = job.result
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                pass
        return jsonify({'success': True, 'result': result})
    elif job.is_failed:
        return jsonify({'success': False, 'error': str(job.exc_info)}), 500
    else:
        return jsonify({'success': False, 'status': job.get_status()}), 202

if __name__ == '__main__':
    app.run(debug=True)
