from dataclasses import asdict, dataclass


@dataclass
class GameSettings:
    #Налаштування гри та загальних параметрів застосунку

    rows: int = 10
    cols: int = 10
    difficulty: int = 5
    cell_size: int = 50
    cell_default_color: str = "#474747"
    cell_open_color: str = "#CDCDCD"
    cell_outline_color: str = "#0006bd"
    flag_color: str = "#0c8628"
    timer: int = 0
    buttons_visible: bool = True
    theme: str = "system"
    extra_dpi: bool = True
    music_volume: float = 0.3
    sfx_volume: float = 0.5

    def as_dict(self) -> dict:
        #Повертає налаштування як словник із зрозумілими ключами
        return asdict(self)

    def apply_theme_cell_colors(self):
        #Встановлює стандартні кольори клітинок залежно від теми
        if self.theme == "light":
            self.cell_default_color = "#A9A9A9"  # Колір клітинок
            self.cell_open_color = "#F6F6F6"    # Колір відкритої клітинки
        else:
            self.cell_default_color = "#474747"  # Колір клітинок
            self.cell_open_color = "#CDCDCD"     # Колір відкритої клітинки


DEFAULT_PRESETS = [
    ["За замовчуванням\n(10x10)", 10, 5, 50],
    ["Мінімальне поле\n(7x7)", 7, 5, 50],
    ["Найлегший\n(7x7)", 7, 1, 50],
    ["Поле 15 клітинок\n(15x15)", 15, 5, 50],
    ["Складність 10\n(10x10)", 10, 10, 50],
    ["Максимум\n(50x50)", 50, 10, 30],
]
