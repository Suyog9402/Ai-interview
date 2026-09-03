import os
import logging
from typing import Optional, Any, Dict, List
from app.core.config import settings

logger = logging.getLogger("llm-provider")


def is_valid_key(key: Optional[str]) -> bool:
    """Check if key is valid and not a placeholder."""
    if not key:
        return False
    k = key.strip()
    if not k or k.startswith("your_") or k.startswith("your-") or "placeholder" in k.lower():
        return False
    return True


def get_groq_key() -> Optional[str]:
    key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    return key if is_valid_key(key) else None


def get_gemini_key() -> Optional[str]:
    key = settings.gemini_api_key or settings.google_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return key if is_valid_key(key) else None


def get_openai_key() -> Optional[str]:
    key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
    return key if is_valid_key(key) else None


def has_any_llm_configured() -> bool:
    """Check if at least one LLM provider (Groq, Gemini, OpenAI) is configured."""
    return bool(get_groq_key() or get_gemini_key() or get_openai_key())


def get_chat_llm(
    temperature: float = 0.3,
    model: Optional[str] = None,
    prefer: str = "groq",
    **kwargs: Any
) -> Optional[Any]:
    """
    Get a LangChain Chat Model with smart fallback across Groq, Gemini, and OpenAI.
    """
    groq_key = get_groq_key()
    gemini_key = get_gemini_key()
    openai_key = get_openai_key()

    # Determine order of providers based on preference and key availability
    providers = []
    if prefer == "groq":
        if groq_key:
            providers.append("groq")
        if gemini_key:
            providers.append("gemini")
        if openai_key:
            providers.append("openai")
    elif prefer == "gemini":
        if gemini_key:
            providers.append("gemini")
        if groq_key:
            providers.append("groq")
        if openai_key:
            providers.append("openai")
    else:
        if openai_key:
            providers.append("openai")
        if groq_key:
            providers.append("groq")
        if gemini_key:
            providers.append("gemini")

    for provider in providers:
        try:
            if provider == "groq":
                from langchain_groq import ChatGroq
                chosen_model = model or getattr(settings, "groq_model", "qwen/qwen3.8-27b")
                return ChatGroq(
                    api_key=groq_key,
                    model=chosen_model,
                    temperature=temperature,
                    **kwargs
                )
            elif provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                chosen_model = model or getattr(settings, "gemini_model", "gemini-2.5-flash")
                return ChatGoogleGenerativeAI(
                    google_api_key=gemini_key,
                    model=chosen_model,
                    temperature=temperature,
                    **kwargs
                )
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                chosen_model = model or getattr(settings, "extraction_model", "gpt-4o")
                return ChatOpenAI(
                    api_key=openai_key,
                    model=chosen_model,
                    temperature=temperature,
                    **kwargs
                )
        except Exception as e:
            logger.warning(f"Failed to initialize {provider} LLM ({e}), trying next provider.")
            continue

    logger.warning("No LLM provider available. Operations requiring AI will use local fallbacks.")
    return None


def get_embeddings() -> Optional[Any]:
    """
    Get vector embeddings model with smart fallback:
    1. Gemini Embeddings (e.g. models/gemini-embedding-001)
    2. OpenAI Embeddings
    3. None (local fallback)
    """
    gemini_key = get_gemini_key()
    if gemini_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            embed_model = getattr(settings, "gemini_embedding_model", "models/gemini-embedding-001")
            return GoogleGenerativeAIEmbeddings(
                google_api_key=gemini_key,
                model=embed_model
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini embeddings ({e})")

    openai_key = get_openai_key()
    if openai_key:
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                api_key=openai_key,
                model="text-embedding-3-small"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI embeddings ({e})")

    return None


def get_deepgram_key() -> Optional[str]:
    key = settings.deepgram_api_key or os.getenv("DEEPGRAM_API_KEY")
    return key if is_valid_key(key) else None


def transcribe_audio_file(file_path: str, language: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Transcribe an audio file with smart fallback across:
    1. Deepgram (Nova-2 / Nova-3: ultra fast, diarization, word timestamps, confidence)
    2. Groq Whisper (whisper-large-v3)
    3. OpenAI Whisper
    4. Gemini multimodal audio
    
    Returns: {
        "text": "...",
        "segments": [...],
        "language": "en",
        "diarization": {...}
    }
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    # 1. Try Deepgram (Primary high-accuracy & diarization provider)
    deepgram_key = get_deepgram_key()
    if deepgram_key:
        try:
            import httpx
            headers = {
                "Authorization": f"Token {deepgram_key}",
            }
            # Detect MIME type
            ext = os.path.splitext(file_path)[1].lower()
            mime_map = {
                ".wav": "audio/wav",
                ".mp3": "audio/mp3",
                ".m4a": "audio/m4a",
                ".webm": "audio/webm",
                ".mp4": "video/mp4",
                ".ogg": "audio/ogg",
                ".flac": "audio/flac"
            }
            mime_type = mime_map.get(ext, "application/octet-stream")
            headers["Content-Type"] = mime_type

            params = {
                "model": getattr(settings, "deepgram_model", "nova-2"),
                "smart_format": "true",
                "diarize": "true",
                "punctuate": "true",
                "utterances": "true",
            }
            if language:
                params["language"] = language

            with open(file_path, "rb") as f:
                audio_bytes = f.read()

            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    "https://api.deepgram.com/v1/listen",
                    headers=headers,
                    params=params,
                    content=audio_bytes
                )

            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", {})
                channels = results.get("channels", [])
                
                transcript_text = ""
                detected_lang = "en"
                if channels and channels[0].get("alternatives"):
                    alt = channels[0]["alternatives"][0]
                    transcript_text = alt.get("transcript", "")
                    detected_lang = alt.get("language", language or "en")
                
                # Extract utterances / diarized segments
                utterances = results.get("utterances", [])
                segments = []
                diarization_data = None

                if utterances:
                    unique_speakers = sorted(list(set(f"speaker_{u.get('speaker', 0)}" for u in utterances)))
                    diarization_segments = []
                    
                    for idx, u in enumerate(utterances):
                        spk = f"speaker_{u.get('speaker', 0)}"
                        seg_text = u.get("transcript", "")
                        start_time = float(u.get("start", 0.0))
                        end_time = float(u.get("end", 0.0))
                        conf = float(u.get("confidence", 0.95))

                        segments.append({
                            "id": idx,
                            "speaker": spk,
                            "start": start_time,
                            "end": end_time,
                            "text": seg_text,
                            "confidence": conf
                        })
                        diarization_segments.append({
                            "speaker": spk,
                            "start": start_time,
                            "end": end_time,
                            "text": seg_text
                        })

                    diarization_data = {
                        "speakers": unique_speakers,
                        "segments": diarization_segments
                    }
                elif channels and channels[0].get("alternatives") and channels[0]["alternatives"][0].get("words"):
                    # Fallback to word chunks
                    words = channels[0]["alternatives"][0]["words"]
                    segments = [{
                        "id": 0,
                        "start": words[0].get("start", 0.0),
                        "end": words[-1].get("end", 0.0),
                        "text": transcript_text,
                        "confidence": sum(w.get("confidence", 0.9) for w in words) / max(len(words), 1)
                    }]

                logger.info(f"Successfully transcribed audio via Deepgram ({len(transcript_text)} chars, {len(segments)} segments)")
                return {
                    "text": transcript_text,
                    "segments": segments,
                    "language": detected_lang,
                    "diarization": diarization_data,
                    "provider": "deepgram"
                }
            else:
                logger.warning(f"Deepgram transcription returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Deepgram transcription failed ({e}), falling back to Groq/OpenAI...")

    # 2. Try Groq Whisper
    groq_key = get_groq_key()
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            whisper_model = getattr(settings, "groq_whisper_model", "whisper-large-v3")
            with open(file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), audio_file.read()),
                    model=whisper_model,
                    response_format="verbose_json"
                )
            
            text = getattr(transcription, "text", "") or ""
            segments = getattr(transcription, "segments", []) or []
            detected_language = getattr(transcription, "language", language or "en") or "en"
            logger.info(f"Successfully transcribed audio via Groq Whisper ({len(text)} chars)")
            return {
                "text": text,
                "segments": segments,
                "language": detected_language,
                "diarization": None,
                "provider": "groq"
            }
        except Exception as e:
            logger.warning(f"Groq Whisper transcription failed ({e}), falling back...")

    # 3. Try OpenAI Whisper
    openai_key = get_openai_key()
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            with open(file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json"
                )
            text = getattr(transcription, "text", "") or ""
            segments = getattr(transcription, "segments", []) or []
            return {
                "text": text,
                "segments": segments,
                "language": getattr(transcription, "language", "en") or "en",
                "diarization": None,
                "provider": "openai"
            }
        except Exception as e:
            logger.warning(f"OpenAI Whisper transcription failed ({e})")

    # 4. Try Gemini multimodal transcription
    gemini_key = get_gemini_key()
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            mime_type = "audio/wav" if file_path.endswith(".wav") else ("audio/mp3" if file_path.endswith(".mp3") else "audio/m4a")
            response = client.models.generate_content(
                model=getattr(settings, "gemini_model", "gemini-2.5-flash"),
                contents=[
                    genai.types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    "Transcribe this audio recording verbatim without adding any introduction or extra commentary."
                ]
            )
            text = response.text.strip() if response.text else ""
            return {
                "text": text,
                "segments": [],
                "language": "en",
                "diarization": None,
                "provider": "gemini"
            }
        except Exception as e:
            logger.warning(f"Gemini audio transcription failed ({e})")

    return None
