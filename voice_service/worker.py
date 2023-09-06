import base64
import json
import os
import re
import wave
from io import BytesIO

import requests
from celery import Celery
from vosk import KaldiRecognizer, Model

celery = Celery(__name__)
celery.conf.broker_url = os.getenv(
    "CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.getenv(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")

model = Model('./vosk-model')
pattern_movie = re.compile(pattern=r"movie\s+([^?!.]+)")
pattern_person = re.compile(pattern=r"person\s+([^?!.]+)")
pattern_genre = re.compile(pattern=r"genre\s+([^?!.]+)")

METHODS = {
    "movie": "api/v1/films/search",
    "person": "api/v1/persons/persons/search",
}


def recognize_audio(file):
    wf = wave.open(file, 'rb')
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    while True:
        data = wf.readframes(8000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    return json.loads(rec.FinalResult())["text"]


@celery.task
def request_async_api(body: bytes):
    decode_body = json.loads(body.decode())
    process_id = decode_body.get("process_id")
    file = decode_body.get("file")
    file_in_memory = BytesIO(base64.b64decode(file.encode()))

    text = recognize_audio(file_in_memory)
    if "movie" in text:
        name = pattern_movie.search(text)
        type_ = "movie"
    elif "genre" in text:
        name = pattern_genre.search(text)
        type_ = "genre"
    elif "person" in text:
        name = pattern_person.search(text)
        type_ = "person"
    else:
        return

    name = name.group(1).strip()
    requests.get(
        f"http://search_service:8000/{METHODS[type_]}",
        params=dict(query=name, process_id=process_id)
    )
