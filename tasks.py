import os
from openai_client import client, api_key
import httpx

def transcribe_audio(filepath, language):
    """Background task to transcribe audio using OpenAI Whisper API."""
    if not api_key:
        return {'success': False, 'error': 'OpenAI API key is not configured.'}
    try:
        with open(filepath, 'rb') as audio_file:
            params = {
                "model": "whisper-1",
                "file": audio_file
            }
            if language and language != 'auto':
                if language == 'zh':
                    params["language"] = "zh"
                elif language == 'en':
                    params["language"] = "en"
            transcript = client.audio.transcriptions.create(**params)
            return {'success': True, 'transcript': transcript.text}
    except httpx.TimeoutException:
        return {'success': False, 'error': 'Network timeout to OpenAI API.'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
