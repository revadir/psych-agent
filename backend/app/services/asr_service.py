import asyncio
import json
import websockets
import base64
from typing import Optional, Callable, Dict, Any
import aiohttp
from app.core.config import settings

class ASRService:
    def __init__(self):
        self.api_key = settings.assemblyai_api_key
        self.base_url = "https://api.assemblyai.com/v2"
        self.ws_url = "wss://api.assemblyai.com/v2/realtime/ws"
        
        # Debug: Check if API key is loaded
        print(f"ASR Service initialized with API key: {'***' + self.api_key[-4:] if self.api_key else 'NOT SET'}")
        
    async def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe an audio file"""
        try:
            # Upload file
            upload_url = await self._upload_file(audio_file_path)
            
            # Request transcription
            transcript_response = await self._request_transcription(upload_url)
            
            # Check if response has required fields
            if 'id' not in transcript_response:
                raise Exception(f"Invalid API response: {transcript_response}")
            
            # Poll for completion
            transcript = await self._poll_transcription(transcript_response['id'])
            
            return {
                'text': transcript.get('text', '') or 'No speech detected in audio',
                'confidence': transcript.get('confidence', 0),
                'words': transcript.get('words', []),
                'speakers': transcript.get('utterances', []) if transcript.get('speaker_labels') else []
            }
        except Exception as e:
            print(f"ASR Service Error: {str(e)}")
            raise
    
    async def start_realtime_transcription(self, 
                                         on_transcript: Callable[[str], None],
                                         on_error: Optional[Callable[[str], None]] = None):
        """Start real-time transcription via WebSocket"""
        try:
            async with websockets.connect(
                f"{self.ws_url}?sample_rate=16000",
                extra_headers={"Authorization": self.api_key}
            ) as websocket:
                
                # Send configuration
                await websocket.send(json.dumps({
                    "sample_rate": 16000,
                    "word_boost": ["therapy", "patient", "diagnosis", "symptoms", "treatment"]
                }))
                
                # Listen for responses
                async for message in websocket:
                    data = json.loads(message)
                    
                    if data['message_type'] == 'FinalTranscript':
                        on_transcript(data['text'])
                    elif data['message_type'] == 'PartialTranscript':
                        on_transcript(data['text'])
                        
        except Exception as e:
            if on_error:
                on_error(str(e))
    
    async def send_audio_chunk(self, websocket, audio_chunk: bytes):
        """Send audio chunk to WebSocket"""
        audio_data = base64.b64encode(audio_chunk).decode("utf-8")
        await websocket.send(json.dumps({
            "audio_data": audio_data
        }))
    
    async def _upload_file(self, file_path: str) -> str:
        """Upload audio file to AssemblyAI"""
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                async with session.post(
                    f"{self.base_url}/upload",
                    headers={"Authorization": self.api_key},
                    data=f
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Upload failed ({response.status}): {error_text}")
                    result = await response.json()
                    if 'upload_url' not in result:
                        raise Exception(f"Invalid upload response: {result}")
                    return result['upload_url']
    
    async def _request_transcription(self, upload_url: str) -> Dict[str, Any]:
        """Request transcription of uploaded file"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/transcript",
                headers={
                    "Authorization": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "audio_url": upload_url,
                    "speaker_labels": True,
                    "punctuate": True,
                    "format_text": True,
                    "word_boost": ["therapy", "patient", "diagnosis", "symptoms", "treatment", "DSM", "ICD"]
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Transcription request failed ({response.status}): {error_text}")
                result = await response.json()
                print(f"Transcription response: {result}")  # Debug log
                return result
    
    async def _poll_transcription(self, transcript_id: str) -> Dict[str, Any]:
        """Poll for transcription completion"""
        async with aiohttp.ClientSession() as session:
            max_attempts = 60  # 3 minutes max
            attempts = 0
            
            while attempts < max_attempts:
                async with session.get(
                    f"{self.base_url}/transcript/{transcript_id}",
                    headers={"Authorization": self.api_key}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Polling failed ({response.status}): {error_text}")
                    
                    result = await response.json()
                    print(f"Poll attempt {attempts + 1}: Status = {result['status']}")
                    
                    if result['status'] == 'completed':
                        print(f"Transcription completed. Text length: {len(result.get('text') or '')}")
                        print(f"Transcribed text: '{result.get('text')}'")
                        return result
                    elif result['status'] == 'error':
                        raise Exception(f"Transcription failed: {result.get('error')}")
                    
                    attempts += 1
                    await asyncio.sleep(3)
            
            raise Exception("Transcription timeout - took longer than 3 minutes")
