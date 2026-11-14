"""Модуль парсинга командной строки."""

from src.constants import QUOTE_CHARS, WHITESPACE


def parse_command(raw_input: str) -> tuple[str, list[str]]:
    """Разбирает строку ввода на имя команды и список аргументов.

    Поддерживает аргументы в кавычках (одинарных и двойных),
    позволяя передавать строки с пробелами как единый аргумент.
    """
    command_name = ""
    arguments: list[str] = []
    current_arg = ""
    in_quotes = False
    quote_char = ""

    # Убираем лишние пробелы по краям
    raw_input = raw_input.strip()

    for char in raw_input:
        if char in QUOTE_CHARS:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = ""
            else:
                current_arg += char
        elif char == WHITESPACE and not in_quotes:
            if current_arg:
                if not command_name:
                    command_name = current_arg
                else:
                    arguments.append(current_arg)
                current_arg = ""
        else:
            current_arg += char

    # Добавляем последний аргумент, если он остался
    if current_arg:
        if not command_name:
            command_name = current_arg
        else:
            arguments.append(current_arg)

    return command_name, arguments
