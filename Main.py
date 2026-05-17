import json
from pathlib import Path
import time

import pyaudio
from vosk import KaldiRecognizer, Model

from Commannds.browser.google import handle_command, type_in_google
from jarvis_remaster.voice import Voice, config


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model_small_ru"
SAMPLE_RATE = 16000
BUFFER_SIZE = 8000
CHUNK_SIZE = 4000

WAKE_WORDS = [
    "ты тут джарвис", "проснись джарвис", "хелло джарвис", "привет джарвис", "включись джарвис", "джарвис ты тут"
]
SLEEP_WORDS = [
    "спокойной ночи джарвис", "пока джарвис", "до свидания джарвис", "выключись джарвис", "можешь выключиться джарвис", "можешь выключится джарвис"
]

voice = Voice(config)


def create_audio_resources():
    model = Model(str(MODEL_PATH))
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=BUFFER_SIZE,
    )
    stream.start_stream()
    return recognizer, audio, stream


def listen(recognizer, stream):
    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)

        if not data:
            continue

        if recognizer.AcceptWaveform(data):
            answer = json.loads(recognizer.Result())
            text = answer.get("text", "").strip()
            if text:
                yield text


def cleanup_audio(stream, audio):
    if stream and stream.is_active():
        stream.stop_stream()
    if stream:
        stream.close()
    if audio:
        audio.terminate()


def cleanup(stream, audio):
    cleanup_audio(stream, audio)
    voice.close()


def main():
    wake_audio = None
    wake_stream = None
    command_audio = None
    command_stream = None

    try:
        wakeRecognizer, wake_audio, wake_stream = create_audio_resources()
        for Waketext in listen(wakeRecognizer, wake_stream):
            Waketext = Waketext.lower().strip()
            if not any(word in Waketext for word in WAKE_WORDS):
                continue

            try:
                recognizer, command_audio, command_stream = create_audio_resources()
                voice.greeting()

                for text in listen(recognizer, command_stream):
                    text = text.lower().strip()
                    if not text:
                        continue

                    print(text)

                    if "спасибо джарвис" in text:
                        voice.get("thanks")
                        continue

                    if type_in_google(text):
                        voice.get("ok")
                        continue

                    if handle_command(text):
                        voice.get("ok")
                        continue

                    if any(word in text for word in SLEEP_WORDS):
                        voice.get("ok")
                        return
            finally:
                cleanup_audio(command_stream, command_audio)
                command_stream = None
                command_audio = None
    except KeyboardInterrupt:
        print("\nJarvis остановлен.")
            
    finally:
        cleanup(wake_stream, wake_audio)


if __name__ == "__main__":
    main()
