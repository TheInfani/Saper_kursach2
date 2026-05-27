import math
import random
from pathlib import Path

import customtkinter as ctk

from game_board import GameBoard
from models import GameSettings
from widgets import AnimatedGif, SoundButton


class GameWindow:
    #Екран гри: інтерфейс, Canvas, обробники миші й клавіатури

    def __init__(self, root: ctk.CTk, app, settings: GameSettings):
        self.root = root
        self.app = app
        self.settings = settings
        self.board = GameBoard(settings)

        self.cell_size = settings.cell_size
        self.num_size = round(self.cell_size / 3)  # Розмір цифр
        self.button_canvas_size = 160 if settings.buttons_visible else 90

        self.selected_row = math.ceil(settings.rows / 2)  # Поточний рядок
        self.selected_col = math.ceil(settings.cols / 2)  # Поточна колонка
        self.first_click = True  # Перевірка першого кліку
        self.is_in_game = True

        self.start_timer = 1  # Час проходження гри
        self.remaining_time = settings.timer
        self.is_timer_on = settings.timer > 0
        self.timer_id = None
        self.start_timer_id = None

        self.canvas = None
        self.mins_label = None
        self.timer_label = None

    def render(self):
        #Створює основне вікно гри
        ctk.set_appearance_mode(self.settings.theme)
        self.app.audio.start_music()

        self.root.deiconify()
        self.root.title("Сапер")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.return_to_menu)

        if self.settings.cols * self.cell_size >= 350:
            width = (self.settings.cols * self.cell_size) + self.settings.cols + 4
            height = (self.settings.rows * self.cell_size) + self.settings.rows + self.button_canvas_size
            self.root.geometry(f"{width}x{height}")
        else:
            self.root.geometry("350x480")

        # Створюємо полотно у верхній частині вікна.
        self.canvas = ctk.CTkCanvas(
            self.root,
            width=(self.settings.cols * self.cell_size) + self.settings.cols + 4,
            height=(self.settings.rows * self.cell_size) + self.settings.rows,
            bg="#242424",
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack(pady=10)

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Button-3>", self.handle_click)

        # Прив'язка стрілок на клавіатурі.
        self.root.bind("<Left>", lambda _event: self.move_left())
        self.root.bind("<Right>", lambda _event: self.move_right())
        self.root.bind("<Up>", lambda _event: self.move_up())
        self.root.bind("<Down>", lambda _event: self.move_down())
        self.root.bind("<F5>", lambda _event: self.debug_window())
        self.root.bind("<s>", lambda _event: self.open_settings_window())
        self.root.bind("<p>", lambda _event: self.pashalka())
        self.root.bind("<Key>", self.keypress)

        self.render_info_panel()
        self.draw_base_field()
        self.draw_selection_outline()
        self.render_control_buttons()
        self.root.focus_set()

    def render_info_panel(self):
        #Верхній інформаційний блок із кількістю прапорців і таймером
        top_info_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        top_info_frame.pack(side=ctk.TOP, pady=5, fill=ctk.X)

        counters_frame = ctk.CTkFrame(top_info_frame, fg_color="transparent")
        counters_frame.pack(side=ctk.TOP)

        self.mins_label = ctk.CTkLabel(
            counters_frame,
            text="Відкрийте першу клітинку",
            font=("Arial", 12),
        )
        self.mins_label.pack(side=ctk.LEFT, padx=15)

        timer_text = f"Час: {self.remaining_time}" if self.is_timer_on else "Час: не встановлено"
        self.timer_label = ctk.CTkLabel(counters_frame, text=timer_text, font=("Arial", 12))
        self.timer_label.pack(side=ctk.LEFT, padx=15)

        instr_label = ctk.CTkLabel(
            top_info_frame,
            text='Ви можете натиснути "S" на клавіатурі під час гри, для зміни налаштувань',
            font=("Arial", 12),
            text_color="gray",
        )
        instr_label.pack(side=ctk.BOTTOM, padx=15)

    def render_control_buttons(self):
        #Кнопки керування знизу. Їх можна вимкнути в налаштуваннях
        if not self.settings.buttons_visible:
            return

        frame_bottom = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_bottom.pack(side=ctk.BOTTOM, fill=ctk.X, pady=10)

        center_frame = ctk.CTkFrame(frame_bottom, fg_color="transparent")
        center_frame.pack(expand=True)

        btn_left = SoundButton(center_frame, text="←", command=self.move_left, audio=self.app.audio, width=50)
        btn_left.pack(side=ctk.LEFT, padx=1)

        frame_ud = ctk.CTkFrame(center_frame, fg_color="transparent")
        frame_ud.pack(side=ctk.LEFT, padx=1)

        btn_up = SoundButton(frame_ud, text="↑", command=self.move_up, audio=self.app.audio, width=50)
        btn_up.pack(side=ctk.TOP, padx=1)

        btn_down = SoundButton(frame_ud, text="↓", command=self.move_down, audio=self.app.audio, width=50)
        btn_down.pack(side=ctk.BOTTOM, padx=1)

        btn_right = SoundButton(center_frame, text="→", command=self.move_right, audio=self.app.audio, width=50)
        btn_right.pack(side=ctk.LEFT, padx=1)

        btn_open = SoundButton(center_frame, text="Відкрити", command=self.scan, audio=self.app.audio, width=70)
        btn_open.pack(side=ctk.LEFT, padx=20)

        btn_flag = SoundButton(
            center_frame,
            text="Прапор",
            command=lambda: self.flag(self.selected_col, self.selected_row),
            audio=self.app.audio,
            width=70,
        )
        btn_flag.pack(side=ctk.LEFT, padx=1)

    # ОТРИСОВКА БАЗОВОГО ПОЛЯ
    def draw_base_field(self):
        #Малює закриті клітинки поля
        x1 = 0
        y1 = 2
        x2 = self.cell_size
        y2 = self.cell_size + 2
        for _row in range(self.settings.rows):
            x1 = 2
            x2 = self.cell_size + 2
            for _col in range(self.settings.cols):
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.settings.cell_default_color,
                )
                x1 = x1 + self.cell_size + 1
                x2 = x2 + self.cell_size + 1
            y1 = y1 + self.cell_size + 1
            y2 = y2 + self.cell_size + 1

    def cell_rect(self, col: int, row: int) -> tuple[int, int, int, int]:
        x1 = col * (self.cell_size + 1) - self.cell_size + 1
        y1 = row * (self.cell_size + 1) - self.cell_size + 1
        return x1, y1, x1 + self.cell_size, y1 + self.cell_size

    def clear_selection_outline(self):
        x1, y1, x2, y2 = self.cell_rect(self.selected_col, self.selected_row)
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=1)
        self.canvas.create_rectangle(x1 - 1, y1 - 1, x2 + 1, y2 + 1, outline="black", width=1)

    def draw_selection_outline(self):
        x1, y1, x2, y2 = self.cell_rect(self.selected_col, self.selected_row)
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.settings.cell_outline_color, width=1)
        self.canvas.create_rectangle(x1 - 1, y1 - 1, x2 + 1, y2 + 1, outline=self.settings.cell_outline_color, width=1)

    # Обробник кліків миші
    def handle_click(self, event):
        if not self.is_in_game:
            return

        # Фікс обводки при використанні кнопок і мишки.
        self.clear_selection_outline()

        max_x = 2 + self.settings.cols * (self.cell_size + 1)
        max_y = 2 + self.settings.rows * (self.cell_size + 1)
        if event.x < 2 or event.x > max_x or event.y < 2 or event.y > max_y:
            self.draw_selection_outline()
            return

        self.selected_col = (event.x - 2) // (self.cell_size + 1) + 1
        self.selected_row = (event.y - 2) // (self.cell_size + 1) + 1

        if event.num == 1:
            self.scan()
        elif event.num == 3:
            self.flag(self.selected_col, self.selected_row)

        self.draw_selection_outline()

    # Альтернатива для української/російської розкладки, бо tkinter не завжди визначає кирилицю.
    def keypress(self, event):
        if event.keycode == 83:  # Клавіша "S"
            self.open_settings_window()

    # ПЕРЕМІЩЕННЯ
    def move_left(self):
        self.app.audio.play_open()
        if self.selected_col > 1:
            self.clear_selection_outline()
            self.selected_col -= 1
            self.draw_selection_outline()

    def move_right(self):
        self.app.audio.play_open()
        if self.selected_col < self.settings.cols:
            self.clear_selection_outline()
            self.selected_col += 1
            self.draw_selection_outline()

    def move_up(self):
        self.app.audio.play_open()
        if self.selected_row > 1:
            self.clear_selection_outline()
            self.selected_row -= 1
            self.draw_selection_outline()

    def move_down(self):
        self.app.audio.play_open()
        if self.selected_row < self.settings.rows:
            self.clear_selection_outline()
            self.selected_row += 1
            self.draw_selection_outline()

    # ВЗАЄМОДІЯ
    def draw_text(self, col: int, row: int, char):
        #Малювання цифр, прапорців і мін на полі
        x = (col * (self.cell_size + 1) - self.cell_size + 1) + (self.cell_size / 2)
        y = (row * (self.cell_size + 1) - self.cell_size + 1) + (self.cell_size / 2)

        if char == "💣":
            x1, y1, x2, y2 = self.cell_rect(col, row)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#940808")
            self.canvas.create_text(x, y, text=str(char), font=("Segoe UI Emoji", self.num_size))
            return

        if char == "🚩":
            color = self.settings.flag_color
        elif int(char) == 1:
            color = "blue"
        elif int(char) == 2:
            color = "green"
        elif int(char) == 3:
            color = "red"
        elif int(char) == 4:
            color = "navy"
        elif int(char) == 5:
            color = "maroon"
        elif int(char) == 6:
            color = "turquoise"
        elif int(char) == 7:
            color = "black"
        else:
            color = "gray"

        self.canvas.create_text(x, y, text=str(char), font=("Arial", self.num_size, "bold"), fill=color)

    def update_mines_label(self):
        self.mins_label.configure(text=f"Прапорів: {self.board.mine_count}")

    def scan(self):
        #Запуск сканування вибраної клітинки
        if not self.is_in_game:
            return

        if self.first_click:
            self.board.remove_mines_around_first_click(self.selected_col, self.selected_row)
            self.update_mines_label()
            self.first_click = False
            if self.is_timer_on:
                self.update_timer()
            self.update_start_timer()

        self.app.audio.play_open()
        self.open_cell(self.selected_col, self.selected_row)

    # Алгоритм відкривання та рекурсія
    def open_cell(self, col: int, row: int):
        if not self.is_in_game:
            return
        if not self.board.in_bounds(col, row):
            return
        if self.board.is_opened(col, row):
            return

        if self.board.is_flagged(col, row):
            self.board.remove_flag_before_open(col, row)
            self.update_mines_label()

        self.board.set_opened(col, row)
        x1, y1, x2, y2 = self.cell_rect(col, row)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.settings.cell_open_color)

        # КІНЕЦЬ ГРИ НА МІНІ
        if self.board.is_mine(col, row):
            self.show_lose_window(lose_from_mine=True)
            self.draw_text(col, row, "💣")
            return

        count = self.board.count_mines_around(col, row)
        if count > 0:
            self.draw_text(col, row, count)
        else:
            # Рекурсивно відкриваємо сусідні клітинки.
            for c in range(col - 1, col + 2):
                for r in range(row - 1, row + 2):
                    if not (c == col and r == row):
                        self.open_cell(c, r)

        if self.is_in_game and self.board.check_win():
            self.show_win_window()

    def flag(self, col: int, row: int):
        #Встановлення або зняття прапорця
        if not self.is_in_game:
            return

        self.app.audio.play_open()
        result = self.board.toggle_flag(col, row)
        if result is True:
            self.draw_text(col, row, "🚩")
        elif result is False:
            x1, y1, x2, y2 = self.cell_rect(col, row)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.settings.cell_default_color)

        if result is not None:
            self.update_mines_label()
            self.draw_selection_outline()

    def update_start_timer(self):
        if self.is_in_game:
            self.start_timer += 1
            self.start_timer_id = self.root.after(1000, self.update_start_timer)

    def update_timer(self):
        if not self.is_in_game or not self.is_timer_on:
            return

        if self.remaining_time <= 0:
            self.show_lose_window(lose_from_mine=False)
            return

        self.remaining_time -= 1
        self.timer_label.configure(text=f"Час: {self.remaining_time}")
        self.timer_id = self.root.after(1000, self.update_timer)

    def stop_timers(self):
        #Зупиняє таймери tkinter, якщо вони були запущені
        for timer_id in (self.timer_id, self.start_timer_id):
            if timer_id is not None:
                try:
                    self.root.after_cancel(timer_id)
                except Exception:
                    pass
        self.timer_id = None
        self.start_timer_id = None

    # Екран перемоги
    def show_win_window(self):
        if not self.is_in_game:
            return

        self.is_in_game = False
        self.app.audio.stop_music()
        self.app.audio.play_win()
        self.stop_timers()

        points = self.calculate_points()
        self.app.storage.add_record(
            points=points,
            time_seconds=self.start_timer,
            difficulty=self.settings.difficulty,
            size=self.settings.rows,
            mines=self.board.start_mine_count,
        )

        win = ctk.CTkToplevel(self.root)
        win.title("Перемога!")
        win.geometry("300x180")
        win.attributes("-topmost", True)
        win.resizable(False, False)

        label = ctk.CTkLabel(win, text=f"Ви перемогли!\nРахунок: {points}", font=("Arial", 14, "bold"))
        label.pack(expand=True)

        btn_new_game = ctk.CTkButton(
            win,
            text="В меню",
            width=10,
            command=lambda: self.return_to_menu(win),
        )
        btn_new_game.pack(side=ctk.BOTTOM, pady=10)

        win.grab_set()
        win.focus_set()
        win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_menu(win))

    def calculate_points(self) -> int:
        #Підрахунок очок за старою формулою, але із захистом від ділення на нуль
        mines = max(1, self.board.start_mine_count)
        difficulty = max(1, self.settings.difficulty)
        game_size = (self.settings.rows + self.settings.cols) / 2
        time_value = max(1, self.start_timer)
        return round(mines * difficulty * game_size / (time_value / (mines * difficulty)))

    # Відкриття всіх мін при поразці
    def open_all_mines(self):
        for col in range(self.settings.cols):
            for row in range(self.settings.rows):
                if self.board.mines[row][col] == 1:
                    self.draw_text(col + 1, row + 1, "💣")

    # Екран поразки
    def show_lose_window(self, lose_from_mine: bool = True):
        if not self.is_in_game:
            return

        self.is_in_game = False
        self.app.audio.stop_music()
        self.app.audio.play_lose()
        self.stop_timers()

        lose = ctk.CTkToplevel(self.root)
        lose.title("Поразка!")
        lose.geometry("300x150")
        lose.attributes("-topmost", True)
        lose.resizable(False, False)

        if lose_from_mine:
            text = "ВИ ПРОГРАЛИ"
        else:
            text = "ЧАС ВИЙШОВ"
        label = ctk.CTkLabel(lose, text=text, font=("Arial", 14, "bold"))
        label.pack(expand=True)

        self.open_all_mines()

        btn_menu = ctk.CTkButton(
            lose,
            text="Нова гра",
            width=10,
            command=lambda: self.restart_same_settings(lose),
        )
        btn_menu.pack(side=ctk.BOTTOM, pady=10)

        lose.grab_set()
        lose.focus_set()
        lose.protocol("WM_DELETE_WINDOW", lambda: self.return_to_menu(lose))

    def restart_same_settings(self, window=None):
        #Починає нову гру без перезапуску Python-процесу
        if window is not None:
            try:
                window.destroy()
            except Exception:
                pass
        self.app.start_game(self.settings)

    def return_to_menu(self, window=None):
        #Повертає користувача в початкове меню без os.execl і без перезапуску коду
        if window is not None:
            try:
                window.destroy()
            except Exception:
                pass
        self.app.show_main_menu()

    # Встановлення всіх прапорців
    def open_all_flags(self):
        for col in range(self.settings.cols):
            for row in range(self.settings.rows):
                if self.board.mines[row][col] == 1 and self.board.flags[row][col] == 0:
                    self.draw_text(col + 1, row + 1, "🚩")
                    self.board.flags[row][col] = 1
                    self.board.mine_count -= 1
                    self.update_mines_label()

    def open_all_unflagged(self):
        for col in range(self.settings.cols):
            for row in range(self.settings.rows):
                if not self.is_in_game:
                    return
                if self.board.flags[row][col] == 0:
                    self.selected_row = row + 1
                    self.selected_col = col + 1
                    self.scan()

    # ФУНКЦІЯ ВІКНА НАЛАГОДЖЕННЯ
    def debug_window(self):
        debug_win = ctk.CTkToplevel(self.root)
        debug_win.title("Debug")
        debug_win.resizable(True, False)
        debug_win.attributes("-topmost", True)

        # Конвертуємо матрицю у табличний вигляд.
        matrix_table = ""
        for row in self.board.mines:
            for cell in row:
                matrix_table += str(cell) + "   "
            matrix_table += "\n"

        label_name = ctk.CTkLabel(debug_win, text="Стартова матриця мін", font=("Arial", 16, "bold"))
        label_name.pack(side=ctk.TOP, pady=25)

        label = ctk.CTkLabel(debug_win, text=matrix_table, font=("Arial", 12, "bold"))
        label.pack(expand=True, padx=25, pady=25)

        button_open = ctk.CTkButton(debug_win, text="Відкрити все", width=10, command=self.open_all_unflagged)
        button_open.pack(side=ctk.BOTTOM, pady=10)

        button_flags = ctk.CTkButton(
            debug_win,
            text="Встановити прапори",
            fg_color="#4CAF50",
            hover_color="#45A049",
            width=10,
            command=self.open_all_flags,
        )
        button_flags.pack(side=ctk.BOTTOM, pady=10)

    def open_settings_window(self):
        from menu_windows import SettingsWindow

        SettingsWindow(self.root, self.app)

    def pashalka(self):
        #Пасхалка з анімованою GIF-картинкою
        gif_path = Path(__file__).resolve().parent / "sounds" / "gif.gif"
        if not gif_path.exists():
            return

        pash_win = ctk.CTkToplevel(self.root)
        pash_win.title("Пасхалка")
        pash_win.resizable(False, False)
        pash_win.attributes("-topmost", True)

        win_w = 220
        win_h = 220
        screen_w = pash_win.winfo_screenwidth()
        screen_h = pash_win.winfo_screenheight()
        random_x = random.randint(0, max(0, screen_w - win_w))
        random_y = random.randint(0, max(0, screen_h - win_h))
        pash_win.geometry(f"{win_w}x{win_h}+{random_x}+{random_y}")

        anim = AnimatedGif(pash_win, gif_path)
        anim.pack(expand=True)

    def destroy(self):
        #Очищення екрана гри перед переходом на інший екран
        self.is_in_game = False
        self.stop_timers()
        self.app.audio.stop_music()

        for sequence in ("<Left>", "<Right>", "<Up>", "<Down>", "<F5>", "<s>", "<p>", "<Key>"):
            try:
                self.root.unbind(sequence)
            except Exception:
                pass
