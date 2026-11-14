"""Главный модуль графического интерфейса эмулятора."""

import argparse
import tkinter as tk
from tkinter import scrolledtext

from src.commands import CommandHandler
from src.constants import (
    DEBUG_CONFIG_FORMAT,
    DEFAULT_VFS_NAME,
    ERR_UNKNOWN_COMMAND,
    WINDOW_HEIGHT,
    WINDOW_TITLE_FORMAT,
    WINDOW_WIDTH,
)
from src.parser import parse_command
from src.script_runner import ScriptRunner
from src.vfs import VirtualFileSystem


class ShellEmulatorApp:
    """Класс графического приложения эмулятора."""

    def __init__(self, root: tk.Tk, vfs_path: str, script_path: str) -> None:
        """Инициализация приложения."""
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs = VirtualFileSystem()
        self.vfs_name = DEFAULT_VFS_NAME

        # Загрузка VFS
        load_error = ""
        if self.vfs_path:
            load_error = self.vfs.load_from_file(self.vfs_path)
            if load_error:
                self.vfs = VirtualFileSystem() 

        self.command_handler = CommandHandler(self.vfs)

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
        self.input_entry.bind("<Return>", self.on_enter_pressed)
        self.input_entry.focus_set()

        self.print_output("Добро пожаловать в эмулятор оболочки!")
        
        if load_error:
            self.print_output(f"ВНИМАНИЕ: {load_error}")

        if self.script_path:
            self.print_output(f"Запуск скрипта: {self.script_path}")
            runner = ScriptRunner(self.script_path, self.execute_command)
            script_error = runner.run()
            if script_error:
                self.print_output(f"ОШИБКА: {script_error}")
            else:
                self.print_output("Скрипт успешно выполнен.")

        self.print_output("Введите 'exit' для выхода.")

    def print_output(self, text: str) -> None:
        """Выводит текст в область истории."""
        if not text:
            return
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def on_enter_pressed(self, event=None) -> None:
        """Обрабатывает нажатие Enter в поле ввода."""
        raw_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        
        if not raw_input.strip():
            return
            
        self.print_output(f"$ {raw_input}")
        command, args = parse_command(raw_input)
        
        if command == "exit":
            self.root.quit()
        else:
            self.execute_command(command, args)

    def execute_command(self, command: str, args: list[str]) -> tuple[bool, str]:
        """Выполняет одну команду. Возвращает успех и сообщение."""
        if command == "vfs-init":
            self.vfs = VirtualFileSystem()
            self.command_handler = CommandHandler(self.vfs)
            self.print_output("VFS сброшена к состоянию по умолчанию.")
            return True, "OK"

        if command == "ls":
            result = self.command_handler.cmd_ls(args)
            self.print_output(result)
            return True, "OK"
            
        if command == "cd":
            result = self.command_handler.cmd_cd(args)
            if result:
                self.print_output(result)
                return False, result
            return True, "OK"
            
        if command == "wc":
            result = self.command_handler.cmd_wc(args)
            self.print_output(result)
            return True, "OK"

        if command == "uniq":
            result = self.command_handler.cmd_uniq(args)
            self.print_output(result)
            return True, "OK"
        
        error_msg = ERR_UNKNOWN_COMMAND.format(command)
        self.print_output(error_msg)
        return False, error_msg


def main() -> None:
    """Запуск приложения с разбором аргументов."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs", default="", help="Путь к VFS")
    parser.add_argument("--script", default="", help="Путь к стартовому скрипту")
    
    args = parser.parse_args()

    print(DEBUG_CONFIG_FORMAT.format("VFS Path", args.vfs))
    print(DEBUG_CONFIG_FORMAT.format("Script Path", args.script))

    root = tk.Tk()
    app = ShellEmulatorApp(root, args.vfs, args.script)
    root.mainloop()


if __name__ == "__main__":
    main()
