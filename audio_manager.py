from pathlib import Path

try:
    import pygame
except ImportError:  # pragma: no cover - залежності встановлюються користувачем
    pygame = None

from models import GameSettings


class AudioManager:
    #Окремий клас для музики та звукових ефектів

    def __init__(self, settings: GameSettings, base_dir: Path | None = None):
        self.settings = settings
        self.base_dir = base_dir or Path(__file__).resolve().parent
        self.sounds_dir = self.base_dir / "sounds"
        self.enabled = False
        self.snd_open = None
        self.snd_lose = None
        self.snd_win = None
        self._init_audio()

    def _init_audio(self):
        #Ініціалізує pygame.mixer, але не ламає програму, якщо звук недоступний
        if pygame is None:
            return

        try:
            pygame.mixer.init()
            self.enabled = True
            self.snd_open = self._load_sound("open.mp3")
            self.snd_lose = self._load_sound("loose.mp3")
            self.snd_win = self._load_sound("win.mp3")
            self.set_sfx_volume(self.settings.sfx_volume)
        except Exception:
            self.enabled = False

    def _load_sound(self, filename: str):
        path = self.sounds_dir / filename
        if not self.enabled or not path.exists():
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except Exception:
            return None

    def start_music(self):
        #Запускає фонову музику гри
        if not self.enabled:
            return

        path = self.sounds_dir / "best_music.mp3"
        if not path.exists():
            return

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(loops=-1)
            pygame.mixer.music.set_volume(self.settings.music_volume)
        except Exception:
            pass

    def stop_music(self):
        #Зупиняє фонову музику
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def set_music_volume(self, value: float):
        self.settings.music_volume = float(value)
        if self.enabled:
            try:
                pygame.mixer.music.set_volume(self.settings.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, value: float):
        self.settings.sfx_volume = float(value)
        for sound in (self.snd_open, self.snd_win, self.snd_lose):
            if sound is not None:
                try:
                    sound.set_volume(self.settings.sfx_volume)
                except Exception:
                    pass

    def play_open(self):
        self._play(self.snd_open)

    def play_win(self):
        self._play(self.snd_win)

    def play_lose(self):
        self._play(self.snd_lose)

    def _play(self, sound):
        if sound is None:
            return
        try:
            sound.play()
        except Exception:
            pass
