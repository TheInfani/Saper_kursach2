from pathlib import Path

import customtkinter as ctk

from audio_manager import AudioManager
from game_window import GameWindow
from menu_windows import GameSettingsMenu, MainMenu
from models import GameSettings
from storage import Storage


class MinesweeperApp:
    #Головний клас застосунку. Він керує екранами та переходами між ними.

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.storage = Storage(self.base_dir)
        self.settings: GameSettings = self.storage.load_settings()

        # Автоматична адаптація до DPI вмикається/вимикається до створення головного вікна.
        if not self.settings.extra_dpi:
            ctk.deactivate_automatic_dpi_awareness()

        ctk.set_appearance_mode(self.settings.theme)
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.audio = AudioManager(self.settings, self.base_dir)
        self.current_screen = None

    def clear_root(self):
        #Очищає головне вікно перед показом нового екрана.
        for widget in self.root.winfo_children():
            widget.destroy()

    def destroy_current_screen(self):
        # Коректно завершує поточний екран, якщо в нього є власне очищення.
        if self.current_screen is not None and hasattr(self.current_screen, "destroy"):
            try:
                self.current_screen.destroy()
            except Exception:
                pass
        self.current_screen = None

    def show_main_menu(self):
        #Показує початкове меню вибору без перезапуску програми.
        self.destroy_current_screen()
        self.clear_root()
        self.current_screen = MainMenu(self.root, self)
        self.current_screen.render()

    def show_game_settings_menu(self):
        #Показує меню налаштувань гри.
        self.destroy_current_screen()
        self.clear_root()
        self.current_screen = GameSettingsMenu(self.root, self)
        self.current_screen.render()

    def start_game(self, settings: GameSettings):
        #Запускає гру з переданими налаштуваннями.
        self.destroy_current_screen()
        self.clear_root()
        self.current_screen = GameWindow(self.root, self, settings)
        self.current_screen.render()

    def run(self):
        #Точка запуску застосунку.
        self.show_main_menu()
        self.root.mainloop()

    def close(self):
        #Закриває програму.
        self.destroy_current_screen()
        self.audio.stop_music()
        self.root.destroy()
