"""Модуль виртуальной файловой системы (VFS)."""

import base64
import json
import os
from typing import Dict, Any, Optional


class VFSNode:
    """Узел файловой системы (файл или папка)."""

    def __init__(self, name: str, is_dir: bool, content: bytes = b"") -> None:
        """Инициализация узла."""
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children: Dict[str, "VFSNode"] = {}

    def add_child(self, child: "VFSNode") -> None:
        """Добавляет дочерний элемент."""
        self.children[child.name] = child


class VirtualFileSystem:
    """Класс для управления VFS."""

    def __init__(self) -> None:
        """Инициализация пустой VFS."""
        self.root = VFSNode("/", is_dir=True)
        self.current_dir = self.root
        self.path_stack: list[str] = []

    def load_from_file(self, filepath: str) -> str:
        """Загружает VFS из JSON-файла. Возвращает текст ошибки или пустую строку."""
        if not os.path.exists(filepath):
            return f"Ошибка загрузки VFS: файл не найден '{filepath}'"

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            return "Ошибка загрузки VFS: неверный формат JSON"

        # Очищаем текущую VFS
        self.root = VFSNode("/", is_dir=True)
        self.current_dir = self.root
        self.path_stack = []

        try:
            self._build_tree(self.root, data["root"])
            return ""
        except Exception as e:
            return f"Ошибка загрузки VFS: {str(e)}"

    def _build_tree(self, parent: VFSNode, node_data: dict) -> None:
        """Рекурсивно строит дерево VFS из словаря."""
        if node_data.get("type") == "directory":
            for name, child_data in node_data.get("children", {}).items():
                if child_data.get("type") == "directory":
                    child = VFSNode(name, is_dir=True)
                    parent.add_child(child)
                    self._build_tree(child, child_data)
                elif child_data.get("type") == "file":
                    encoded = child_data.get("content", "")
                    try:
                        content = base64.b64decode(encoded)
                    except Exception:
                        content = encoded.encode("utf-8")
                    child = VFSNode(name, is_dir=False, content=content)
                    parent.add_child(child)

    def get_prompt_path(self) -> str:
        """Возвращает текущий путь для отображения (например, /home/user)."""
        if not self.path_stack:
            return "/"
        return "/" + "/".join(self.path_stack)
