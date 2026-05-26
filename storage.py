import json
from pathlib import Path
from typing import Any

from models import DEFAULT_PRESETS, GameSettings


class Storage:
    #Робота з файлами налаштувань, пресетів і рекордів

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent
        self.settings_path = self.base_dir / "settings.json"
        self.old_settings_path = self.base_dir / "settings.txt"
        self.presets_path = self.base_dir / "presets.json"
        self.records_path = self.base_dir / "records.json"
        
    def load_settings(self) -> GameSettings:
        #Завантажує налаштування зі словника у JSON. Старий settings.txt читається тільки для сумісності
        settings = GameSettings()
        
        if self.settings_path.exists():
            try:
                data = json.loads(self.settings_path.read_text(encoding="utf-8"))
                for key, value in data.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
                return settings
            except Exception:
                return settings

        # Сумісність зі старим форматом: music, sfx, buttons, theme, extra_dpi.
        if self.old_settings_path.exists():
            try:
                lines = self.old_settings_path.read_text(encoding="utf-8").splitlines()
                if len(lines) >= 5:
                    settings.music_volume = float(lines[0].strip())
                    settings.sfx_volume = float(lines[1].strip())
                    settings.buttons_visible = lines[2].strip() == "True"
                    settings.theme = lines[3].strip() or "system"
                    settings.extra_dpi = lines[4].strip() == "True"
                    settings.apply_theme_cell_colors()
            except Exception:
                pass

        return settings

    def save_settings(self, settings: GameSettings):
        #Зберігає налаштування як словник із ключами, а не як список за індексами
        self.settings_path.write_text(
            json.dumps(settings.as_dict(), ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

    def load_presets(self) -> list[list[Any]]:
        #Завантажує пресети налаштувань гри
        if not self.presets_path.exists():
            return [preset.copy() for preset in DEFAULT_PRESETS]

        try:
            data = json.loads(self.presets_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else [preset.copy() for preset in DEFAULT_PRESETS]
        except Exception:
            return [preset.copy() for preset in DEFAULT_PRESETS]

    def save_presets(self, presets: list[list[Any]]):
        #Зберігає список пресетів
        self.presets_path.write_text(
            json.dumps(presets, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

    def load_records(self) -> list[list[Any]]:
        #Завантажує рекорди та сортує їх за кількістю очок
        if not self.records_path.exists():
            return []

        try:
            data = json.loads(self.records_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            data.sort(key=lambda record: record[0], reverse=True)
            return data
        except Exception:
            return []

    def save_records(self, records: list[list[Any]]):
        #Зберігає рекорди
        self.records_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

    def add_record(self, points: int, time_seconds: int, difficulty: int, size: int, mines: int):
        #Додає рекорд або замінює старий, якщо новий результат кращий
        records = self.load_records()
        existing_record = None

        # Шукаємо рекорд з такими самими параметрами складності й розміру поля.
        for record in records:
            if len(record) >= 4 and record[2] == difficulty and record[3] == size:
                existing_record = record
                break

        new_record = [points, time_seconds, difficulty, size, mines]
        if existing_record is None:
            records.append(new_record)
        elif points > existing_record[0]:
            records.remove(existing_record)
            records.append(new_record)

        records.sort(key=lambda record: record[0], reverse=True)
        self.save_records(records)
