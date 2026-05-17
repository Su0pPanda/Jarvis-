import os
import random
import time
import tomllib
from datetime import datetime
from pathlib import Path

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pygame import mixer


BASE_DIR = Path(__file__).resolve().parent

with (BASE_DIR / "voice.toml").open("rb") as f:
    config = tomllib.load(f)

voice_id = config["voice"]["id"]
voice_name = config["voice"]["name"]
languages = config["voice"]["languages"]


class Voice:
    def __init__(self, config):
        self.config = config
        self.reactions = config["reactions"]["ru"]
        self.base_path = BASE_DIR / "ru"

    def _ensure_mixer(self):
        if not mixer.get_init():
            mixer.init()

    def get(self, reaction_type):
        phrases = self.reactions.get(reaction_type, [])
        key = random.choice(phrases) if phrases else None

        if key is None:
            return None

        self._ensure_mixer()
        mixer.music.load(str(self.base_path / f"{key}.mp3"))
        mixer.music.play()

        started_at = time.time()
        while mixer.music.get_busy():
            if time.time() - started_at > 15:
                mixer.music.stop()
                break
            time.sleep(0.1)

        return key

    def greeting(self):
        hour = datetime.now().hour

        if 4 <= hour < 12:
            key = "greet_morning"
        elif 12 <= hour < 17:
            key = "greet_day"
        elif 17 <= hour < 20:
            key = "greet_evening"
        else:
            key = "greet_night"

        self.get(key)

    def close(self):
        if mixer.get_init():
            mixer.quit()


voice = Voice(config)

if __name__ == "__main__":
    voice.get("ok")
