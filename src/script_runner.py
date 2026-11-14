"""Модуль для чтения и выполнения стартовых скриптов."""

import os
from typing import Callable, Optional

from src.constants import ERR_SCRIPT_ERROR
from src.parser import parse_command


class ScriptRunner:
    """Класс для выполнения команд из скрипта."""

    def __init__(self, script_path: str, command_handler: Callable) -> None:
        """Инициализация с путём к скрипту и обработчиком команд."""
        self.script_path = script_path
        self.command_handler = command_handler

    def run(self) -> Optional[str]:
        """Выполняет скрипт построчно. Возвращает текст ошибки или None."""
        if not self.script_path or not os.path.exists(self.script_path):
            return f"Файл скрипта не найден: {self.script_path}"

        with open(self.script_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                # Убираем пробелы и пропускаем пустые строки
                raw_command = line.strip()
                if not raw_command:
                    continue

                command, args = parse_command(raw_command)
                
                # Вызываем обработчик (это будет метод из GUI)
                is_success, message = self.command_handler(command, args)
                
                if not is_success:
                    return ERR_SCRIPT_ERROR.format(line_number, message)

        return None
