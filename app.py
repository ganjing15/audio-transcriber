import os
import tempfile
from flask import Flask, render_template, request, jsonify, url_for
from redis import Redis
from rq import Queue
import tasks
import time
import json
from werkzeug.utils import secure_filename
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OPENAI_API_KEY is not set in the environment variables")
    print("Please make sure you have a .env file with a valid API key")

print(f"API Key available: {bool(api_key)}")
if api_key:
    print(f"API Key starts with: {api_key[:5]}...")

# Create OpenAI client with increased timeout
try:
    client = OpenAI(
        api_key=api_key
    )
    
    # Configure the httpx client with a longer timeout
    import httpx
    try:
        # Use more forgiving timeouts and retries for unstable connections
        client.http_client = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=30.0, read=30.0, write=30.0, pool=30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        print("Configured httpx client with extended timeouts")
    except Exception as e:
        print(f"Warning: Could not configure httpx client: {e}")
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    import traceback
    print(traceback.format_exc())

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
ction.") from timeout_err
                        except Exception as e:
                            # For other errors, don't retry
                            print(f"API call failed with error: {e}")
                            raise
                    
                    # Print for debugging
                    print(f"Transcript response type: {type(transcript)}")
                    print(f"Transcript content: {transcript}")
                    
                    # Get the transcript text - handle both object and dict formats
                    transcript_text = None
                    if hasattr(transcript, 'text'):
                        transcript_text = transcript.text
                        print(f"Retrieved text from transcript object: {transcript_text[:50]}...")
                    elif isinstance(transcript, dict) and 'text' in transcript:
                        transcript_text = transcript['text']
                        print(f"Retrieved text from transcript dict: {transcript_text[:50]}...")
                    else:
                        transcript_text = str(transcript)
                        print(f"Converted transcript to string: {transcript_text[:50]}...")
            except Exception as e:
                # If API call fails, fall back to demo mode
                print(f"API call failed, falling back to demo mode. Error: {e}")
                app.config['OFFLINE_DEMO_MODE'] = True  # Force demo mode after failure
                return upload_file()  # Recursively call this function in demo mode
        
        # Clean up the temporary file
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted temporary file: {filepath}")
        
        # Return the transcription with clear structure
        print("Sending successful response")
        return jsonify({
            'success': True,
            'transcript': transcript_text
        })
        
    except Exception as e:
        # Log the error with full traceback
        import traceback
        print(f"FILE UPLOAD ERROR: {str(e)}")
        print(traceback.format_exc())
        
        # Clean up the temporary file if it exists
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
