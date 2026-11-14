"""Главный модуль графического интерфейса эмулятора."""

import tkinter as tk
from tkinter import scrolledtext

from src.constants import (
    DEFAULT_VFS_NAME,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_TITLE_FORMAT,
)
from src.parser import parse_command


class ShellEmulatorApp:
    """Класс графического приложения эмулятора."""

    def __init__(self, root: tk.Tk, vfs_name: str) -> None:
        """Инициализация приложения."""
        self.root = root
        self.vfs_name = vfs_name

        # Настройка окна
        self.root.title(WINDOW_TITLE_FORMAT.format(self.vfs_name))
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Область вывода (история)
        self.output_area = scrolledtext.ScrolledText(
            self.root, state=tk.DISABLED, wrap=tk.WORD
        )
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Область ввода
        self.input_entry = tk.Entry(self.root)
        self.input_entry.pack(padx=10, pady=10, fill=tk.X)
        self.input_entry.bind("<Return>", self.process_input)
        self.input_entry.focus()

        self.print_output("Добро пожаловать в эмулятор оболочки!")
        self.print_output("Введите 'exit' для выхода.")

    def print_output(self, text: str) -> None:
        """Выводит текст в область истории."""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def process_input(self, event=None) -> None:
        """Обрабатывает ввод пользователя."""
        raw_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)

        if not raw_input.strip():
            return

        self.print_output(f"$ {raw_input}")

        command, args = parse_command(raw_input)

        if command == "exit":
            self.root.quit()
            return

        if command == "ls" or command == "cd":
            self.print_output(f"Команда: {command}, Аргументы: {args}")
        else:
            self.print_output(f"Ошибка: неизвестная команда '{command}'")


def main() -> None:
    """Запуск приложения."""
    root = tk.Tk()
    app = ShellEmulatorApp(root, DEFAULT_VFS_NAME)
    root.mainloop()


if __name__ == "__main__":
    main()
