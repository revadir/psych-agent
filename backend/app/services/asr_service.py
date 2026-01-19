import asyncio
import json
import websockets
import base64
from typing import Optional, Callable, Dict, Any
import aiohttp
from app.core.config import settings

class ASRService:
    def __init__(self):
        self.api_key = getattr(settings, 'assemblyai_api_key', None)
        self.base_url = "https://api.assemblyai.com/v2"
        self.ws_url = "wss://api.assemblyai.com/v2/realtime/ws"
        
    async def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe an audio file"""
        try:
            upload_url = await self._upload_file(audio_file_path)
            transcript_response = await self._request_transcription(upload_url)
            
            if 'id' not in transcript_response:
                raise Exception(f"Invalid API response: {transcript_response}")
            
            transcript = await self._poll_transcription(transcript_response['id'])
            
            return {
                'text': transcript.get('text', '') or 'No speech detected in audio',
                'confidence': transcript.get('confidence', 0),
                'words': transcript.get('words', []),
                'speakers': transcript.get('utterances', []) if transcript.get('speaker_labels') else []
            }
        except Exception as e:
            raise
    
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
                return result
    
    async def _poll_transcription(self, transcript_id: str) -> Dict[str, Any]:
        """Poll for transcription completion"""
        async with aiohttp.ClientSession() as session:
            max_attempts = 60
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
                    
                    if result['status'] == 'completed':
                        return result
                    elif result['status'] == 'error':
                        raise Exception(f"Transcription failed: {result.get('error')}")
                    
                    attempts += 1
                    await asyncio.sleep(3)
            
            raise Exception("Transcription timeout - took longer than 3 minutes")
