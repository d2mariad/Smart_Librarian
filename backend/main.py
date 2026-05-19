from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI, BadRequestError
from fastapi.staticfiles import StaticFiles
import base64
import os
from uuid import uuid4

from app import ask_smart_librarian

from app import ask_smart_librarian, contains_offensive_language

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/audio", exist_ok=True)
os.makedirs("static/images", exist_ok=True)


class ChatRequest(BaseModel):
    message: str


class TTSRequest(BaseModel):
    text: str


class ImageRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "backend works"}


@app.post("/chat")
def chat(request: ChatRequest):
    if contains_offensive_language(request.message):
        return {
            "response": "Te rog să formulezi întrebarea într-un mod respectuos.",
            "title": "",
            "visual_hint": "",
        }

    return ask_smart_librarian(request.message)


@app.post("/generate-image")
def generate_image(request: ImageRequest):
    prompt = request.prompt.lower()

    if any(term in prompt for term in ["magical", "castle school", "floating candles", "owl", "spell books"]):
        fallback_prompt = (
            "Create an original cinematic fantasy illustration. "
            "Show three young students inside an ancient magical castle school, with floating candles, glowing books, "
            "enchanted corridors, warm torchlight, mystery, and a strong sense of friendship and wonder. "
            "Highly detailed, dramatic lighting, emotionally rich, visually striking. "
            "No text, no typography, no copyrighted names, no actor likenesses."
        )
    elif any(term in prompt for term in ["habit", "discipline", "personal growth", "routine"]):
        fallback_prompt = (
            "Create an elegant conceptual editorial illustration about personal growth, discipline, and habit building. "
            "Show one person improving life through small consistent routines, with subtle visual metaphors for progress, focus, and clarity. "
            "Warm light, refined composition, polished modern style. "
            "No text, no typography."
        )
    elif any(term in prompt for term in ["dystopian", "surveillance", "giant screens", "oppressive architecture"]):
        fallback_prompt = (
            "Create a dark cinematic dystopian illustration with a solitary figure in a surveillance-controlled city, "
            "cold atmosphere, giant screens, dramatic shadows, and oppressive architecture. "
            "Highly atmospheric and emotionally powerful. "
            "No text, no typography."
        )
    elif any(term in prompt for term in ["desert world", "monumental dunes", "futuristic structures", "destiny"]):
        fallback_prompt = (
            "Create an epic science-fiction illustration of a lone hero on a vast desert world, "
            "with monumental dunes, dramatic sky, mystical light, and distant futuristic structures. "
            "Cinematic, detailed, and visually grand. "
            "No text, no typography."
        )
    else:
        fallback_prompt = (
            "Create a cinematic story-inspired illustration with a distinctive setting, strong atmosphere, dramatic lighting, "
            "rich visual detail, and emotional depth. "
            "Make it feel polished and memorable, not generic. "
            "No text, no typography, no title, no author name, no book cover layout."
        )

    try:
        try:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=request.prompt,
                size="1024x1024",
            )
        except BadRequestError:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=fallback_prompt,
                size="1024x1024",
            )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        image_path = f"static/images/{uuid4()}.png"
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        return {"image_url": f"http://127.0.0.1:8000/{image_path}"}

    except BadRequestError:
        raise HTTPException(
            status_code=400,
            detail="Promptul imaginii a fost blocat chiar și după fallback.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la generarea imaginii: {str(e)}",
        )

@app.post("/tts")
def text_to_speech(request: TTSRequest):
    try:
        speech_file = f"static/audio/{uuid4()}.mp3"

        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=request.text,
        )

        response.stream_to_file(speech_file)
        return {"audio_url": f"http://127.0.0.1:8000/{speech_file}"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la generarea audio: {str(e)}",
        )


@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    temp_path = f"static/audio/{uuid4()}_{audio.filename}"

    try:
        with open(temp_path, "wb") as f:
            f.write(await audio.read())

        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file,
            )

        return {"text": transcript.text}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la transcriere: {str(e)}",
        )


app.mount("/static", StaticFiles(directory="static"), name="static")