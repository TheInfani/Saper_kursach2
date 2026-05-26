import random

from models import GameSettings


class GameBoard:
    #Модель ігрового поля: міни, відкриті клітинки та прапорці

    def __init__(self, settings: GameSettings) -> None:
        self.settings = settings
        self.rows = settings.rows
        self.cols = settings.cols
        self.difficulty = settings.difficulty
        self.mines: list[list[int]] = []
        self.opened: list[list[int]] = []
        self.flags: list[list[int]] = []
        self.mine_count = 0
        self.start_mine_count = 0
        self.generate()

    def generate(self) -> None:
        #Створює матрицю мін і службові матриці стану клітинок
        self.mines = []
        self.mine_count = 0
        inverted_difficulty = 11 - self.difficulty

        # СТВОРЕННЯ МАТРИЦІ МІН
        for _row in range(self.rows):
            row = []
            for _col in range(self.cols):
                if random.randint(0, inverted_difficulty) == 1:
                    row.append(1)
                    self.mine_count += 1
                else:
                    row.append(0)
            self.mines.append(row)

        # Якщо мін вийшло занадто мало, додаємо їх вручну.
        while self.mine_count < self.difficulty:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if self.mines[row][col] == 0:
                self.mines[row][col] = 1
                self.mine_count += 1

        self.start_mine_count = self.mine_count
        self.opened = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.flags = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def in_bounds(self, col: int, row: int) -> bool:
        #Перевіряє, чи клітинка знаходиться всередині поля. Координати 1-based
        return 1 <= col <= self.cols and 1 <= row <= self.rows

    def remove_mines_around_first_click(self, col: int, row: int) -> int:
        #Перший клік безпечний: прибираємо міни біля першої відкритої клітинки
        removed = 0
        for c in range(col - 1, col + 2):
            for r in range(row - 1, row + 2):
                if self.in_bounds(c, r) and self.mines[r - 1][c - 1] == 1:
                    self.mines[r - 1][c - 1] = 0
                    removed += 1

        self.mine_count -= removed
        self.start_mine_count = self.mine_count
        return removed

    def count_mines_around(self, col: int, row: int) -> int:
        #СКАНУВАННЯ НАВКОЛО КЛІТИНКИ: рахує кількість мін поруч
        number = 0
        for c in range(col - 1, col + 2):
            for r in range(row - 1, row + 2):
                if self.in_bounds(c, r) and self.mines[r - 1][c - 1] == 1:
                    number += 1
        return number

    def is_mine(self, col: int, row: int) -> bool:
        return self.mines[row - 1][col - 1] == 1

    def is_opened(self, col: int, row: int) -> bool:
        return self.opened[row - 1][col - 1] == 1

    def is_flagged(self, col: int, row: int) -> bool:
        return self.flags[row - 1][col - 1] == 1

    def set_opened(self, col: int, row: int) -> None:
        self.opened[row - 1][col - 1] = 1

    def toggle_flag(self, col: int, row: int) -> bool | None:
        #Ставить або прибирає прапорець. Повертає True, якщо прапорець поставлено
        if not self.in_bounds(col, row) or self.is_opened(col, row):
            return None

        if self.flags[row - 1][col - 1] == 0:
            self.flags[row - 1][col - 1] = 1
            self.mine_count -= 1
            return True

        self.flags[row - 1][col - 1] = 0
        self.mine_count += 1
        return False

    def remove_flag_before_open(self, col: int, row: int) -> None:
        #Якщо відкриваємо клітинку з прапорцем, прапорець прибирається
        if self.flags[row - 1][col - 1] == 1:
            self.flags[row - 1][col - 1] = 0
            self.mine_count += 1

    def check_win(self) -> bool:
        #Перевірка перемоги: відкриті всі клітинки без мін
        total_cells = self.rows * self.cols
        mine_cells = sum(row.count(1) for row in self.mines)
        opened_cells = sum(row.count(1) for row in self.opened)
        return opened_cells == total_cells - mine_cells
