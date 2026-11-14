"""Модуль реализации команд оболочки."""

from src.vfs import VirtualFileSystem, VFSNode


class CommandHandler:
    """Обработчик команд, работающий с VFS."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        """Инициализация с текущей VFS."""
        self.vfs = vfs

    def _resolve_path(self, path_str: str) -> VFSNode | None:
        """Находит узел по строковому пути."""
        if not path_str or path_str == ".":
            return self.vfs.current_dir
        if path_str == "..":
            if not self.vfs.path_stack:
                return self.vfs.root
            parent_path = self.vfs.path_stack[:-1]
            return self._find_node_by_stack(self.vfs.root, parent_path)

        if path_str == "/":
            return self.vfs.root
            
        parts = path_str.strip("/").split("/")
        current = self.vfs.root if path_str.startswith("/") else self.vfs.current_dir
        return self._find_node_by_stack(current, parts)

    def _find_node_by_stack(self, start_node: VFSNode, parts: list[str]) -> VFSNode | None:
        """Проходит по дереву и ищет узел."""
        current = start_node
        for part in parts:
            if not part:
                continue
            if not current.is_dir or part not in current.children:
                return None
            current = current.children[part]
        return current

    def cmd_ls(self, args: list[str]) -> str:
        """Реализация команды ls."""
        target = self.vfs.current_dir
        if args:
            target = self._resolve_path(args[0])
            if not target:
                return f"ls: cannot access '{args[0]}': No such file or directory"
                
        if not target.is_dir:
            return target.name

        result = []
        for name, node in target.children.items():
            suffix = "/" if node.is_dir else ""
            result.append(name + suffix)
        
        return "  ".join(sorted(result))

    def cmd_cd(self, args: list[str]) -> str:
        """Реализация команды cd."""
        if not args:
            self.vfs.current_dir = self.vfs.root
            self.vfs.path_stack = []
            return ""

        path_str = args[0]
        target = self._resolve_path(path_str)
        
        if not target:
            return f"cd: {path_str}: No such file or directory"
        if not target.is_dir:
            return f"cd: {path_str}: Not a directory"

        # Обновляем состояние
        if path_str.startswith("/"):
            self.vfs.path_stack = [p for p in path_str.split("/") if p]
        elif path_str == "..":
            if self.vfs.path_stack:
                self.vfs.path_stack.pop()
        else:
            self.vfs.path_stack.extend([p for p in path_str.split("/") if p])
        
        self.vfs.current_dir = target
        return ""

    def cmd_wc(self, args: list[str]) -> str:
        """Реализация команды wc (строки, слова, байты)."""
        if not args:
            return "wc: missing file operand"
            
        target = self._resolve_path(args[0])
        if not target or target.is_dir:
            return f"wc: {args[0]}: No such file or directory"
            
        text = target.content.decode("utf-8", errors="replace")
        lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        words = len(text.split())
        chars = len(text)
        
        return f"{lines} {words} {chars} {args[0]}"

    def cmd_uniq(self, args: list[str]) -> str:
        """Реализация команды uniq (удаление повторяющихся строк)."""
        if not args:
            return "uniq: missing file operand"
            
        target = self._resolve_path(args[0])
        if not target or target.is_dir:
            return f"uniq: {args[0]}: No such file or directory"
            
        text = target.content.decode("utf-8", errors="replace")
        lines = text.splitlines()
        unique_lines = []
        prev = None
        for line in lines:
            if line != prev:
                unique_lines.append(line)
                prev = line
                
        return "\n".join(unique_lines)
        
    def cmd_rmdir(self, args: list[str]) -> str:
        """Реализация команды rmdir (удаление пустой папки)."""
        if not args:
            return "rmdir: missing operand"
            
        path_str = args[0]
        target = self._resolve_path(path_str)
        
        if not target:
            return f"rmdir: failed to remove '{path_str}': No such file or directory"
        if not target.is_dir:
            return f"rmdir: failed to remove '{path_str}': Not a directory"
        if target.children:
            return f"rmdir: failed to remove '{path_str}': Directory not empty"
        if path_str == "/" or path_str == ".":
            return "rmdir: cannot remove current or root directory"

        # Удаляем папку из родительской
        parent_path = path_str.strip("/").split("/")[:-1]
        if not path_str.startswith("/"):
            parent_path = self.vfs.path_stack + parent_path
            
        parent = self._find_node_by_stack(self.vfs.root, parent_path)
        if parent and target.name in parent.children:
            del parent.children[target.name]
            
        return ""
