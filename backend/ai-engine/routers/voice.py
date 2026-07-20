from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io

router = APIRouter(prefix="/ai", tags=["Voice IO"])

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        content = await audio.read()
        
        # We need an AudioFile compatible stream, which usually means WAV format
        with sr.AudioFile(io.BytesIO(content)) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            
        return {"status": "success", "text": text}
    except ImportError:
        raise HTTPException(status_code=500, detail="SpeechRecognition module not installed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transcription failed: {str(e)}")

@router.get("/speak")
async def speak_text(text: str):
    try:
        from gtts import gTTS
        
        if not text:
            raise HTTPException(status_code=400, detail="Text parameter is required")
            
        tts = gTTS(text=text, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    except ImportError:
        raise HTTPException(status_code=500, detail="gTTS module not installed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
