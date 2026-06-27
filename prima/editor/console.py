from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit
from PyQt5.QtCore import Qt


class ConsolePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(500)
        self.output.setStyleSheet("background: #1e1e1e; color: #d4d4d4; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.output)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type command here...")
        self.input.setStyleSheet("background: #252526; color: #d4d4d4; font-family: monospace; padding: 4px;")
        self.input.returnPressed.connect(self._execute)
        layout.addWidget(self.input)

        self.write("Prima Engine Console ready.\n")

    def write(self, text):
        self.output.appendPlainText(text)

    def _execute(self):
        cmd = self.input.text().strip()
        self.input.clear()
        if cmd:
            self.write(f"> {cmd}")
            self._eval_command(cmd)

    def _eval_command(self, cmd):
        parts = cmd.split()
        if not parts:
            return
        command = parts[0].lower()

        if command in ("help", "?"):
            self.write("  Commands: help, clear, list, select, move, rotate, size, color, new, delete")
        elif command == "clear":
            self.output.clear()
        elif command == "list":
            self.write("  Use hierarchy panel to browse objects")
        elif command in ("select", "move", "rotate", "size", "color"):
            self.write(f"  TODO: {command} command not yet implemented in console")
        else:
            self.write(f"  Unknown command: {command}. Type 'help' for commands.")
