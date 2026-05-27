import webbrowser
from typing import Any

import customtkinter as ctk

from models import GameSettings
from widgets import ErrorWindow, SoundButton


class MainMenu:
    #Початкове меню вибору дії

    def __init__(self, root: ctk.CTk, app):
        self.root = root
        self.app = app

    def render(self):
        self.root.deiconify()
        self.root.title("Головне меню")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.app.close)

        label = ctk.CTkLabel(self.root, text="Сапер Офлайн", font=("Arial", 16, "bold"))
        label.pack(pady=15)

        single_btn = SoundButton(
            self.root,
            text="Почати гру",
            fg_color=("#4CAF50", "#2E7D32"),
            hover_color=("#66BB6A", "#388E3C"),
            command=self.app.show_game_settings_menu,
            audio=self.app.audio,
        )
        single_btn.pack(pady=10)

        github_btn = SoundButton(
            self.root,
            text="GitHub проєкту",
            fg_color=("#D6D6D6", "#8A8A8A"),
            hover_color=("#C0C0C0", "#707070"),
            command=lambda: webbrowser.open_new_tab("https://github.com/TheInfani/Saper_kursach2"),
            audio=self.app.audio,
        )
        github_btn.pack(pady=10)

        settings_btn = SoundButton(
            self.root,
            text="Налаштування",
            fg_color=("#9E9E9E", "#5F5F5F"),
            hover_color=("#B0B0B0", "#707070"),
            command=lambda: SettingsWindow(self.root, self.app),
            audio=self.app.audio,
        )
        settings_btn.pack(pady=10)

        records_btn = SoundButton(
            self.root,
            text="Рекорди",
            fg_color=("#42A5F5", "#1565C0"),
            hover_color=("#64B5F6", "#1976D2"),
            command=lambda: RecordsWindow(self.root, self.app),
            audio=self.app.audio,
        )
        records_btn.pack(pady=10)

    def destroy(self):
        pass


class GameSettingsMenu:
    #Меню налаштувань гри перед запуском партії

    def __init__(self, root: ctk.CTk, app):
        self.root = root
        self.app = app
        self.settings = app.settings
        self.presets_data = app.storage.load_presets()

        self.size_entry = None
        self.difficulty_entry = None
        self.cell_size_entry = None
        self.timer_entry = None
        self.preview_canvas = None
        self.lbl_recommended = None
        self.scroll_pres_frame = None
        self.scroll_del_frame = None
        self.preset_name_entry = None

        self.cell_default_color = self.settings.cell_default_color
        self.cell_open_color = self.settings.cell_open_color
        self.cell_outline_color = self.settings.cell_outline_color
        self.flag_color = self.settings.flag_color

    def render(self):
        self.root.title("Меню налаштувань гри")
        self.root.geometry("900x670")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.app.show_main_menu)

        # Лівий фрейм
        frame_left = ctk.CTkFrame(self.root, width=300, height=670, corner_radius=0, fg_color="transparent")
        frame_left.pack(side="left")
        frame_left.pack_propagate(False)

        label = ctk.CTkLabel(frame_left, text="Налаштування гри", font=("Arial", 16, "bold"))
        label.pack(pady=5)

        # Визначаємо розмір поля.
        label = ctk.CTkLabel(frame_left, text="Розмір поля в клітинках (від 7 до 50)")
        label.pack(pady=5)
        self.size_entry = ctk.CTkEntry(frame_left)
        self.size_entry.insert(0, str(self.settings.rows))
        self.size_entry.pack(pady=5)

        # Визначаємо складність.
        label = ctk.CTkLabel(frame_left, text="Складність (від 1 до 10)")
        label.pack(pady=5)
        self.difficulty_entry = ctk.CTkEntry(frame_left)
        self.difficulty_entry.insert(0, str(self.settings.difficulty))
        self.difficulty_entry.pack(pady=5)

        # Визначаємо розмір клітинки.
        label = ctk.CTkLabel(frame_left, text="Розмір клітинки в пікселях (від 10)")
        label.pack(pady=5)
        self.cell_size_entry = ctk.CTkEntry(frame_left)
        self.cell_size_entry.insert(0, str(self.settings.cell_size))
        self.cell_size_entry.pack(pady=5)

        # Рекомендація щодо максимального розміру поля залежно від розміру клітинки та екрана.
        self.lbl_recommended = ctk.CTkLabel(frame_left, text="", text_color="red", font=("Arial", 12, "bold"))
        self.lbl_recommended.pack(pady=0)
        self.calculate_max_size()

        # Визначаємо таймер.
        label = ctk.CTkLabel(frame_left, text="Час на проходження гри\n(в секундах, 0 - без таймера)")
        label.pack(pady=5)
        self.timer_entry = ctk.CTkEntry(frame_left)
        self.timer_entry.insert(0, str(self.settings.timer))
        self.timer_entry.pack(pady=5)

        # Визначаємо колір клітинок за замовчуванням.
        label = ctk.CTkLabel(frame_left, text="Колір клітинок за замовчуванням")
        label.pack(pady=5)
        btn = SoundButton(frame_left, text="Вибрати колір", command=lambda: self.choose_color("default"), audio=self.app.audio)
        btn.pack(pady=5)

        # Визначаємо колір відкритих клітинок.
        label = ctk.CTkLabel(frame_left, text="Колір відкритих клітинок")
        label.pack(pady=5)
        btn2 = SoundButton(frame_left, text="Вибрати колір", command=lambda: self.choose_color("open"), audio=self.app.audio)
        btn2.pack(pady=5)

        # Визначаємо колір активної обводки.
        label = ctk.CTkLabel(frame_left, text="Колір активної обводки")
        label.pack(pady=5)
        btn3 = SoundButton(frame_left, text="Вибрати колір", command=lambda: self.choose_color("outline"), audio=self.app.audio)
        btn3.pack(pady=5)

        # Визначаємо колір прапорця.
        label = ctk.CTkLabel(frame_left, text="Колір прапорця")
        label.pack(pady=5)
        btn4 = SoundButton(frame_left, text="Вибрати колір", command=lambda: self.choose_color("flag"), audio=self.app.audio)
        btn4.pack(pady=5)

        back_btn = SoundButton(frame_left, text="Назад", command=self.app.show_main_menu, audio=self.app.audio)
        back_btn.pack(side=ctk.BOTTOM, pady=10)

        # Правий фрейм
        frame_right = ctk.CTkFrame(self.root, width=300, height=670, corner_radius=0, fg_color="transparent")
        frame_right.pack(side="right")
        frame_right.pack_propagate(False)

        label = ctk.CTkLabel(frame_right, text="Попередній перегляд поля", font=("Arial", 16, "bold"))
        label.pack(pady=10)

        self.preview_canvas = ctk.CTkCanvas(frame_right, width=280, height=200, bg="#929292", highlightthickness=0, borderwidth=0)
        self.preview_canvas.pack(pady=20)

        label = ctk.CTkLabel(
            frame_right,
            text="Якщо не встановити налаштування,\nбудуть застосовані параметри\nза замовчуванням",
        )
        label.pack(pady=10)

        label = ctk.CTkLabel(
            frame_right,
            text="Вводьте значення в форматі\nцілих чисел без одиниць виміру",
            font=("Arial", 14),
            text_color="red",
        )
        label.pack(pady=10)

        btn_try = SoundButton(frame_right, text="Випробувати", command=self.try_preview, audio=self.app.audio)
        btn_try.pack(side=ctk.BOTTOM, pady=10)

        btn_start = SoundButton(frame_right, text="Старт", command=self.start_game, audio=self.app.audio)
        btn_start.pack(side=ctk.BOTTOM, pady=10)

        # Фрейм пресетів налаштувань.
        frame_presets = ctk.CTkFrame(self.root, width=300, height=670, fg_color="transparent", border_width=0, corner_radius=0)
        frame_presets.pack(side="right")
        frame_presets.pack_propagate(False)

        frame_list = ctk.CTkFrame(frame_presets, width=300, height=550, fg_color="transparent", corner_radius=0)
        frame_list.pack(side="top")
        frame_list.pack_propagate(False)

        label = ctk.CTkLabel(frame_list, text="Пресети налаштувань", font=("Arial", 16, "bold"))
        label.pack(pady=10)

        # Створюємо область з прокручуванням.
        self.scroll_pres_frame = ctk.CTkScrollableFrame(
            frame_list,
            width=180,
            height=550,
            border_width=0,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color="#BABABA",
        )
        self.scroll_pres_frame.pack(pady=5, padx=5, fill="both", expand=True)
        self.scroll_pres_frame._scrollbar.configure(width=0)
        self.refresh_presets()

        # Фрейм видалення пресетів.
        frame_del_btn = ctk.CTkFrame(frame_presets, width=300, height=30, fg_color="transparent", border_width=0, corner_radius=0)
        frame_del_btn.pack(side=ctk.BOTTOM, pady=5, padx=25)
        frame_del_btn.pack_propagate(False)

        del_btn = ctk.CTkButton(
            frame_del_btn,
            text="Меню видалення пресетів",
            command=self.window_presets_delete,
            width=250,
            fg_color="#A30000",
            hover_color="#7A0000",
        )
        del_btn.pack()

        add_button = ctk.CTkButton(frame_presets, text="Додати свій пресет", command=self.add_preset, width=250)
        add_button.pack(side=ctk.BOTTOM, pady=5)

        self.preset_name_entry = ctk.CTkEntry(frame_presets, width=250)
        self.preset_name_entry.insert(0, "Назва пресету")
        self.preset_name_entry.pack(side=ctk.BOTTOM, pady=5)

        self.try_preview()

    def read_form_values(self) -> tuple[int, int, int, int] | None:
        #Читає та перевіряє основні числові поля
        try:
            cell_size = int(self.cell_size_entry.get())
            difficulty = int(self.difficulty_entry.get())
            rows = int(self.size_entry.get())
            timer = int(self.timer_entry.get())
        except ValueError:
            ErrorWindow(self.root, "Введено некоректний тип даних", "350x100", audio=self.app.audio)
            return None

        if rows < 7 or rows > 50:
            ErrorWindow(self.root, "Введіть розмір поля в діапазоні від 7 до 50", "450x100", audio=self.app.audio)
            return None
        if difficulty < 1 or difficulty > 10:
            ErrorWindow(self.root, "Введіть складність в\nдіапазоні від 1 до 10", "300x120", audio=self.app.audio)
            return None
        if cell_size < 10:
            ErrorWindow(self.root, "Введіть розмір\nклітинки більше 10", "230x120", audio=self.app.audio)
            return None
        if timer < 0 or timer > 3600:
            ErrorWindow(self.root, "Введіть додатне значення часу,\nчи 0 для відключення таймера", "400x120", audio=self.app.audio)
            return None

        return rows, difficulty, cell_size, timer

    # Відрисовка тестового відображення клітинок.
    def try_preview(self):
        values = self.read_form_values()
        if values is None:
            return

        _rows, _difficulty, cell_size, _timer = values
        self.preview_canvas.delete("all")
        self.preview_canvas.create_rectangle(100, 100, 100 + cell_size, 100 + cell_size, fill=self.cell_open_color)
        self.preview_canvas.create_rectangle(100, 100, 100 + cell_size, 100 + cell_size, outline="black", width=1)
        self.preview_canvas.create_rectangle(99, 99, 100 + cell_size + 1, 100 + cell_size + 1, outline="black", width=1)
        self.preview_canvas.create_rectangle(102 + cell_size, 100, 102 + cell_size + cell_size, 100 + cell_size, fill=self.cell_default_color)
        self.preview_canvas.create_rectangle(102 + cell_size, 100, 102 + cell_size + cell_size, 100 + cell_size, outline=self.cell_outline_color, width=1)
        self.preview_canvas.create_rectangle(102 + cell_size, 99, 102 + cell_size + cell_size + 1, 100 + cell_size + 1, outline=self.cell_outline_color, width=1)
        self.preview_canvas.create_text(102 + cell_size + cell_size / 2, 98 + cell_size / 2, text="🚩", font=("Arial", round(cell_size / 3), "bold"), fill=self.flag_color)
        self.preview_canvas.create_text(100 + cell_size / 2, 100 + cell_size / 2, text="1", font=("Arial", round(cell_size / 3), "bold"), fill="blue")

        self.calculate_max_size()

    def choose_color(self, color_name: str):
        #Одна функція замість чотирьох майже однакових функцій вибору кольору
        try:
            from CTkColorPicker import AskColor
        except ImportError:
            ErrorWindow(self.root, "Модуль CTkColorPicker не встановлено", "360x100", audio=self.app.audio)
            return

        color = AskColor().get()
        if not color:
            return

        if color_name == "default":
            self.cell_default_color = color
        elif color_name == "open":
            self.cell_open_color = color
        elif color_name == "outline":
            self.cell_outline_color = color
        elif color_name == "flag":
            self.flag_color = color

        self.try_preview()

    def start_game(self):
        values = self.read_form_values()
        if values is None:
            return

        rows, difficulty, cell_size, timer = values
        self.settings.rows = rows
        self.settings.cols = rows
        self.settings.difficulty = difficulty
        self.settings.cell_size = cell_size
        self.settings.cell_default_color = self.cell_default_color
        self.settings.cell_open_color = self.cell_open_color
        self.settings.cell_outline_color = self.cell_outline_color
        self.settings.flag_color = self.flag_color
        self.settings.timer = timer
        self.settings.buttons_visible = self.app.settings.buttons_visible
        self.settings.theme = self.app.settings.theme

        self.app.storage.save_settings(self.settings)
        self.app.start_game(self.settings)

    # Функція для розрахунку максимального рекомендованого розміру поля.
    def calculate_max_size(self):
        try:
            cell_size = int(self.cell_size_entry.get())
            if cell_size > 0:
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                max_safe = min((screen_w - 54) // (cell_size + 1), (screen_h - 200) // (cell_size + 1))
                self.lbl_recommended.configure(text=f"Макс. рекомендований розмір поля: {max_safe}")
        except Exception:
            pass

    def apply_preset(self, preset_size: Any, preset_difficulty: Any, preset_cell: Any):
        #Застосовує пресет до полів введення
        self.size_entry.delete(0, ctk.END)
        self.size_entry.insert(0, str(preset_size))
        self.difficulty_entry.delete(0, ctk.END)
        self.difficulty_entry.insert(0, str(preset_difficulty))
        self.cell_size_entry.delete(0, ctk.END)
        self.cell_size_entry.insert(0, str(preset_cell))
        self.try_preview()

    def refresh_presets(self):
        #Оновлює список пресетів
        for widget in self.scroll_pres_frame.winfo_children():
            widget.destroy()

        for preset in self.presets_data:
            preset_button = ctk.CTkButton(
                self.scroll_pres_frame,
                text=preset[0],
                command=lambda value=preset: self.apply_preset(value[1], value[2], value[3]),
                height=60,
                width=250,
            )
            preset_button.pack(pady=5)

    def add_preset(self):
        p_size = self.size_entry.get()
        p_diff = self.difficulty_entry.get()
        p_cell = self.cell_size_entry.get()
        name = self.preset_name_entry.get().strip()

        if name == "" or name == "Назва пресету":
            preset_name = f"Пресет {len(self.presets_data) + 1}\n({p_size}x{p_size})"
        else:
            preset_name = f"{name}\n({p_size}x{p_size})"

        self.presets_data.append([preset_name, p_size, p_diff, p_cell])
        self.app.storage.save_presets(self.presets_data)
        self.refresh_presets()

    def window_presets_delete(self):
        #Вікно видалення пресетів
        w_delete = ctk.CTkToplevel(self.root)
        w_delete.title("Видалення пресетів")
        w_delete.geometry("300x670")
        w_delete.resizable(False, False)
        w_delete.attributes("-topmost", True)

        frame_pres_del = ctk.CTkFrame(w_delete, width=300, height=600, fg_color="transparent", border_width=0, corner_radius=0)
        frame_pres_del.pack(side="right")
        frame_pres_del.pack_propagate(False)

        label = ctk.CTkLabel(frame_pres_del, text="Натисніть на пресет\nдля видалення", font=("Arial", 16, "bold"))
        label.pack(pady=5)

        self.scroll_del_frame = ctk.CTkScrollableFrame(
            frame_pres_del,
            width=300,
            height=600,
            border_width=0,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
        )
        self.scroll_del_frame.pack(pady=5, padx=5, fill="both", expand=True)
        self.scroll_del_frame._scrollbar.configure(width=0)
        self.refresh_delete_presets()

    def refresh_delete_presets(self):
        for widget in self.scroll_del_frame.winfo_children():
            widget.destroy()

        for preset in self.presets_data:
            btn = ctk.CTkButton(
                self.scroll_del_frame,
                text=preset[0],
                height=60,
                width=250,
                fg_color="#A30000",
                hover_color="#7A0000",
                command=lambda value=preset: self.delete_preset(value),
            )
            btn.pack(pady=5)

    def delete_preset(self, preset_to_delete: list[Any]):
        if preset_to_delete in self.presets_data:
            self.presets_data.remove(preset_to_delete)
        self.app.storage.save_presets(self.presets_data)
        self.refresh_delete_presets()
        self.refresh_presets()

    def destroy(self):
        pass


class SettingsWindow(ctk.CTkToplevel):
    #Загальні налаштування: звук, тема, кнопки керування, DPI

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.settings: GameSettings = app.settings

        self.title("Налаштування")
        self.geometry("350x650")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        label = ctk.CTkLabel(self, text="ЗВУКИ", font=("Arial", 16, "bold"))
        label.pack(pady=15)

        label = ctk.CTkLabel(self, text="Гучність музики:", font=("Arial", 14))
        label.pack(pady=10)
        slider_music = ctk.CTkSlider(self, from_=0.0, to=1.0, number_of_steps=20, command=self.update_music_volume)
        slider_music.set(self.settings.music_volume)
        slider_music.pack(pady=5)

        label = ctk.CTkLabel(self, text="Гучність ефектів:", font=("Arial", 14))
        label.pack(pady=10)
        slider_sfx = ctk.CTkSlider(self, from_=0.0, to=1.0, number_of_steps=20, command=self.update_sfx_volume)
        slider_sfx.set(self.settings.sfx_volume)
        slider_sfx.pack(pady=15)

        label = ctk.CTkLabel(
            self,
            text='Ви можете натиснути "S" на клавіатурі\nпід час гри, для зміни налаштувань',
            font=("Arial", 12),
            text_color="gray",
        )
        label.pack(pady=10)

        label = ctk.CTkLabel(self, text="ЗАГАЛЬНЕ", font=("Arial", 16, "bold"))
        label.pack(pady=15)

        buttons_var = ctk.BooleanVar(value=self.settings.buttons_visible)
        buttons_checkbox = ctk.CTkCheckBox(
            self,
            text="Увімкнути відображення кнопок",
            variable=buttons_var,
            onvalue=True,
            offvalue=False,
            command=lambda: self.update_buttons_visible(buttons_var.get()),
        )
        buttons_checkbox.pack(pady=6)

        label = ctk.CTkLabel(self, text="Зміниться в наступній грі", font=("Arial", 12), text_color="gray")
        label.pack(pady=5)

        dpi_var = ctk.BooleanVar(value=self.settings.extra_dpi)
        dpi_checkbox = ctk.CTkCheckBox(
            self,
            text="Увімкнути автоматичну адаптацію до DPI",
            variable=dpi_var,
            onvalue=True,
            offvalue=False,
            command=lambda: self.update_dpi(dpi_var.get()),
        )
        dpi_checkbox.pack(pady=6)

        label = ctk.CTkLabel(self, text="Зміниться після перезапуску програми", font=("Arial", 12), text_color="gray")
        label.pack(pady=5)

        theme_var = ctk.StringVar(value=self.settings.theme)
        ctk.CTkRadioButton(self, text="Системна тема", variable=theme_var, value="system", command=lambda: self.update_theme(theme_var.get())).pack(pady=6)
        ctk.CTkRadioButton(self, text="Світла тема", variable=theme_var, value="light", command=lambda: self.update_theme(theme_var.get())).pack(pady=6)
        ctk.CTkRadioButton(self, text="Темна тема", variable=theme_var, value="dark", command=lambda: self.update_theme(theme_var.get())).pack(pady=6)

        label = ctk.CTkLabel(
            self,
            text='"Права" на музику належать YarikGamarnik\nДякую Nek0Anim3 за зведення',
            font=("Arial", 12),
            text_color="gray",
        )
        label.pack(pady=20)

    def update_music_volume(self, value: float):
        self.app.audio.set_music_volume(float(value))
        self.app.storage.save_settings(self.settings)

    def update_sfx_volume(self, value: float):
        self.app.audio.set_sfx_volume(float(value))
        self.app.audio.play_open()
        self.app.storage.save_settings(self.settings)

    def update_buttons_visible(self, value: bool):
        self.settings.buttons_visible = bool(value)
        self.app.storage.save_settings(self.settings)

    def update_dpi(self, value: bool):
        self.settings.extra_dpi = bool(value)
        self.app.storage.save_settings(self.settings)

    def update_theme(self, value: str):
        self.settings.theme = value
        ctk.set_appearance_mode(value)
        self.settings.apply_theme_cell_colors()
        self.app.storage.save_settings(self.settings)


class RecordsWindow(ctk.CTkToplevel):
    #Вікно таблиці рекордів

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.records_data = app.storage.load_records()

        self.title("Рекорди")
        self.geometry("300x670")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        frame_records = ctk.CTkFrame(self, width=300, height=670, fg_color="transparent", border_width=0, corner_radius=0)
        frame_records.pack(side="right")
        frame_records.pack_propagate(False)

        frame_record_list = ctk.CTkFrame(frame_records, width=300, height=570, fg_color="transparent")
        frame_record_list.pack(side="top")
        frame_record_list.pack_propagate(False)

        label = ctk.CTkLabel(frame_record_list, text="Рекорди", font=("Arial", 16, "bold"))
        label.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(frame_record_list, width=180, height=500, border_width=0, corner_radius=0, fg_color="transparent", scrollbar_fg_color="transparent")
        scroll_frame.pack(pady=5, padx=5, fill="both", expand=True)
        scroll_frame._scrollbar.configure(width=0)

        if not self.records_data:
            label_empty = ctk.CTkLabel(scroll_frame, text="Рекордів поки немає", font=("Arial", 12))
            label_empty.pack(pady=20)
            return

        # Таблиця рекордів: очки, час проходження, складність, розмір, кількість мін.
        for record in self.records_data:
            if len(record) < 5:
                continue
            record_button = ctk.CTkButton(
                scroll_frame,
                text=f"Очок: {record[0]}  Час (секунди): {record[1]}\nСкладність: {record[2]}  Розмір поля: {record[3]}  Мін: {record[4]}",
                height=60,
            )
            record_button.pack(pady=5, fill="x")
