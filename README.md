# Audio Transcriber

A simple web application that transcribes M4A audio files to text using OpenAI's Whisper API. This app can be run locally or deployed to Render for use in regions with restricted API access.

## Features

- Easy-to-use web interface with drag-and-drop functionality
- Supports M4A audio files
- Real-time upload progress tracking
- Copy transcription to clipboard functionality

## Requirements

- Python 3.6+
- OpenAI API key

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and go to `http://127.0.0.1:5000/`
3. Upload an M4A audio file using the interface
4. Click "Transcribe Audio" to process the file
5. View the transcription result and copy it to your clipboard if needed

## Notes

- This application currently only supports M4A audio files.
- File size is limited to 16MB due to OpenAI API limitations.
- The quality of transcription depends on the audio quality and the speech clarity.

## Deployment to Render

This application can be deployed to Render to ensure API connectivity in regions with restricted access to OpenAI's API (like mainland China).

### Automatic Deployment

1. Create a new Web Service in your Render dashboard
2. Connect your GitHub repository containing this code
3. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add your `OPENAI_API_KEY` as an environment variable
5. Click Deploy

### Manual Deployment

1. Push this code to a Git repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Web Service"
4. Connect your Git repository
5. Configure the following settings:
   - Name: audio-transcriber (or your preferred name)
   - Environment: Python
   - Region: Choose a region outside of China for optimal API connectivity
   - Branch: main (or your default branch)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. Add your `OPENAI_API_KEY` as an environment variable
7. Click "Create Web Service"

After deployment, you'll receive a URL where you can access your application from anywhere, including regions with API restrictions.
