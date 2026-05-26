from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image, ImageSequence


class SoundButton(ctk.CTkButton):
    #Кнопка зі стандартним виглядом і звуком натискання

    def __init__(
        self,
        master,
        text: str,
        command: Callable,
        audio=None,
        width: int = 110,
        height: int = 25,
        fg_color=("#D9D8D8", "#515151"),
        hover_color=("#BABABA", "#373737"),
        text_color=("black", "white"),
    ) -> None:
        self.audio = audio

        def command_with_sound():
            if self.audio is not None:
                self.audio.play_open()
            command()

        super().__init__(
            master=master,
            text=text,
            command=command_with_sound,
            width=width,
            height=height,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
        )


class ErrorWindow(ctk.CTkToplevel):
    #Невелике модальне вікно з повідомленням про помилку

    def __init__(self, master, error_text: str, size: str, audio=None) -> None:
        super().__init__(master)
        self.title("Помилка")
        self.geometry(size)
        self.resizable(False, False)
        self.attributes("-topmost", True)

        label = ctk.CTkLabel(self, text=error_text, font=("Arial", 16, "bold"))
        label.pack(expand=True, pady=10)

        btn = SoundButton(self, text="Ок", command=self.destroy, audio=audio)
        btn.pack(side="bottom", pady=10)

        self.grab_set()
        self.focus_set()


class AnimatedGif(ctk.CTkLabel):
    #Віджет для відображення анімованої GIF-картинки

    def __init__(self, master, path: str | Path) -> None:
        self.path = Path(path)
        self.img = Image.open(self.path)
        self.frames = [
            ctk.CTkImage(light_image=frame.copy(), dark_image=frame.copy(), size=(200, 200))
            for frame in ImageSequence.Iterator(self.img)
        ]
        super().__init__(master, image=self.frames[0], text="")
        self.current_frame = 0
        self.animate()

    def animate(self) -> None:
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.configure(image=self.frames[self.current_frame])
        self.after(60, self.animate)
