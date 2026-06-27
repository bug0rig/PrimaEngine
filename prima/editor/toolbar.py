from PyQt5.QtWidgets import (
    QToolBar, QAction, QFileDialog, QMessageBox,
    QSpinBox, QLabel, QInputDialog, QLineEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from prima.server.serialize import scene_to_dict, scene_from_dict
from prima.server.protocol import ProtocolMessage
from prima.server.client import GameClient
import json
import os
import socket


class EditorToolbar(QToolBar):
    def __init__(self, editor_window, parent=None):
        super().__init__("Tools", parent)
        self.editor = editor_window
        self.setMovable(False)

        self._add_action("New Scene", self._new_scene, "Ctrl+N")
        self._add_action("Save Scene", self._save_scene, "Ctrl+S")
        self._add_action("Load Scene", self._load_scene, "Ctrl+O")
        self.addSeparator()

        self._add_action("Undo", lambda: None, "Ctrl+Z")
        self._add_action("Redo", lambda: None, "Ctrl+Shift+Z")
        self.addSeparator()

        self._play_action = self._add_action("Play", self._play_scene, "F5")
        self._add_action("Stop", self._stop_scene, "Shift+F5")
        self.addSeparator()

        self._add_action("Reset Camera", self._reset_camera, "F")
        self._add_action("Focus Selected", self._focus_selected, "Shift+F")
        self.addSeparator()
        self._add_action("Upload to Server...", self._upload_to_server)

    def _add_action(self, name, callback, shortcut=None):
        action = QAction(name, self)
        action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        self.addAction(action)
        return action

    def _new_scene(self):
        self.editor.engine.scene = Scene()
        self.editor.viewport.selected_object = None
        self.editor.hierarchy.refresh()
        self.editor.properties.show_object(None)

    def _save_scene(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Scene", "", "Prima Scene (*.prima)")
        if not path:
            return
        if not path.endswith('.prima'):
            path += '.prima'
        try:
            data = scene_to_dict(self.editor.engine.scene)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")

    def _load_scene(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Scene", "", "Prima Scene (*.prima)")
        if not path:
            return
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            scene = scene_from_dict(data)
            self.editor.engine.set_scene(scene)
            self.editor.viewport.selected_object = None
            self.editor.hierarchy.refresh()
            self.editor.properties.show_object(None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load: {e}")

    def _play_scene(self):
        from prima.runtime.player import RuntimeWindow
        if hasattr(self, '_runtime_window') and self._runtime_window and self._runtime_window.isVisible():
            return
        data = scene_to_dict(self.editor.engine.scene)
        scene = scene_from_dict(data)
        self._runtime_window = RuntimeWindow(scene)
        self._runtime_window.show()
        self.editor.statusBar().showMessage("Runtime: WASD=move, Mouse=look, Esc=exit", 5000)

    def _stop_scene(self):
        if hasattr(self, '_runtime_window') and self._runtime_window:
            self._runtime_window.close()
            self._runtime_window = None
        self.editor.statusBar().showMessage("Runtime stopped", 3000)

    def _upload_to_server(self):
        host, ok = QInputDialog.getText(self, "Upload Scene", "Server host:")
        if not ok or not host:
            return
        port, ok = QInputDialog.getInt(self, "Upload Scene", "Port:", 5777, 1024, 65535)
        if not ok:
            return
        session, ok = QInputDialog.getText(self, "Upload Scene", "Session name:", text="default")
        if not ok:
            return

        try:
            client = GameClient()
            client.connect(host, port, session, "__uploader__")
            joined = client.wait_for("joined", timeout=5)
            if joined is None:
                QMessageBox.critical(self, "Upload Error", "Could not join server")
                return

            scene_data = scene_to_dict(self.editor.engine.scene)
            client.send(ProtocolMessage.make_upload_scene(session, scene_data))
            ack = client.wait_for("scene_uploaded", timeout=5)
            if ack is None:
                QMessageBox.critical(self, "Upload Error", "Server did not confirm upload")
                return

            client.disconnect()
            QMessageBox.information(self, "Upload Complete",
                f"Scene uploaded to {host}:{port} session '{session}'")
            self.editor.statusBar().showMessage(f"Uploaded to {host}:{port}/{session}", 3000)
        except (socket.error, ConnectionRefusedError, TimeoutError) as e:
            QMessageBox.critical(self, "Upload Error", str(e))

    def _reset_camera(self):
        self.editor.viewport.reset_camera()

    def _focus_selected(self):
        self.editor.viewport.focus_on(self.editor.viewport.selected_object)
