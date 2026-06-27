"""Game client window — connects to a Prima server, renders the scene, relays input."""

import math
import time

from PyQt5.QtWidgets import (
    QMainWindow, QOpenGLWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox, QApplication,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QFont
from OpenGL import GL

from prima.engine.camera import build_view_matrix, build_projection_matrix
from prima.engine.math_utils import Vector3
from prima.engine.core import Engine
from prima.server.client import GameClient
from prima.server.protocol import ProtocolMessage
from prima.server.serialize import scene_from_dict


class ConnectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Server")
        self.setMinimumWidth(320)

        layout = QFormLayout(self)
        self.host_edit = QLineEdit("127.0.0.1")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(5777)
        self.session_edit = QLineEdit("default")
        self.name_edit = QLineEdit("Player")

        layout.addRow("Host:", self.host_edit)
        layout.addRow("Port:", self.port_spin)
        layout.addRow("Session:", self.session_edit)
        layout.addRow("Name:", self.name_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def connect_info(self):
        return (
            self.host_edit.text(),
            self.port_spin.value(),
            self.session_edit.text(),
            self.name_edit.text(),
        )


class GameViewport(QOpenGLWidget):
    orbited = pyqtSignal()

    def __init__(self, engine, client, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.client = client
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        self.cam_position = Vector3(5, 3, 5)
        self.cam_rotation = Vector3(math.radians(-20), math.radians(-135), 0)
        self.move_speed = 8.0
        self.mouse_sensitivity = 0.003
        self.keys = set()
        self._mouse_captured = False
        self._last_mx = 0
        self._last_my = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

        self._state_timer = QTimer(self)
        self._state_timer.timeout.connect(self._poll_server)
        self._state_timer.start(16)

    def initializeGL(self):
        GL.glClearColor(0.15, 0.15, 0.18, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        self.engine.initialize()

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)

    def paintGL(self):
        self.engine.update()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        aspect = self.width() / max(self.height(), 1)
        view = build_view_matrix(self.cam_position, self.cam_rotation)
        proj = build_projection_matrix(70, aspect, 0.01, 1000)
        self.engine.render(view, proj, self.cam_position)

    def _tick(self):
        forward = Vector3(
            math.sin(self.cam_rotation.y), 0, math.cos(self.cam_rotation.y)
        ).normalized()
        right = Vector3(
            -math.cos(self.cam_rotation.y), 0, math.sin(self.cam_rotation.y)
        ).normalized()

        speed = self.move_speed * self.engine.delta_time
        moved = False
        if Qt.Key_W in self.keys:
            self.cam_position = self.cam_position + forward * speed; moved = True
        if Qt.Key_S in self.keys:
            self.cam_position = self.cam_position - forward * speed; moved = True
        if Qt.Key_A in self.keys:
            self.cam_position = self.cam_position - right * speed; moved = True
        if Qt.Key_D in self.keys:
            self.cam_position = self.cam_position + right * speed; moved = True
        if Qt.Key_Space in self.keys:
            self.cam_position.y += speed; moved = True
        if Qt.Key_Shift in self.keys:
            self.cam_position.y -= speed; moved = True

        self.update()

    def _poll_server(self):
        for msg in self.client.poll():
            if msg.type == "state":
                self._apply_state(msg.data.get("objects", []))

    def _apply_state(self, objects: list[dict]):
        for obj_data in objects:
            scene_obj = self.engine.scene.find_by_id(obj_data["id"])
            if scene_obj is None:
                continue
            pos = obj_data["position"]
            rot = obj_data["rotation"]
            sz = obj_data["size"]
            if scene_obj.position.x != pos[0] or scene_obj.position.y != pos[1] or scene_obj.position.z != pos[2]:
                scene_obj.position = Vector3(*pos)
            if scene_obj.rotation.x != rot[0] or scene_obj.rotation.y != rot[1] or scene_obj.rotation.z != rot[2]:
                scene_obj.rotation = Vector3(*rot)
            if scene_obj.size.x != sz[0] or scene_obj.size.y != sz[1] or scene_obj.size.z != sz[2]:
                scene_obj.size = Vector3(*sz)

    def _send_input(self):
        actions = {}
        if Qt.Key_W in self.keys: actions["forward"] = True
        if Qt.Key_S in self.keys: actions["backward"] = True
        if Qt.Key_A in self.keys: actions["left"] = True
        if Qt.Key_D in self.keys: actions["right"] = True
        if Qt.Key_Space in self.keys: actions["jump"] = True
        if actions:
            self.client.send(ProtocolMessage.make_input(actions))

    def keyPressEvent(self, event: QKeyEvent):
        self.keys.add(event.key())
        self._send_input()
        if event.key() == Qt.Key_Escape:
            if self._mouse_captured:
                self._mouse_captured = False
                self.setCursor(Qt.ArrowCursor)
                self.releaseMouse()
            else:
                self.window().close()

    def keyReleaseEvent(self, event: QKeyEvent):
        self.keys.discard(event.key())
        self._send_input()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            self._mouse_captured = True
            self._last_mx = event.x()
            self._last_my = event.y()
            self.setCursor(Qt.BlankCursor)
            self.grabMouse()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton and self._mouse_captured:
            self._mouse_captured = False
            self.setCursor(Qt.ArrowCursor)
            self.releaseMouse()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._mouse_captured:
            return
        dx = event.x() - self._last_mx
        dy = event.y() - self._last_my
        if dx == 0 and dy == 0:
            return
        self._last_mx = event.x()
        self._last_my = event.y()
        self.cam_rotation.y -= dx * self.mouse_sensitivity
        self.cam_rotation.x -= dy * self.mouse_sensitivity
        self.cam_rotation.x = max(-math.pi / 2 + 0.01, min(math.pi / 2 - 0.01, self.cam_rotation.x))
        self.orbited.emit()

    def closeEvent(self, event):
        self._timer.stop()
        self._state_timer.stop()
        self.client.disconnect()
        self.engine.shutdown()
        event.accept()


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prima - Game Client")
        self.setMinimumSize(800, 600)

        self.client = GameClient()

        connect = ConnectDialog(self)
        if connect.exec_() != QDialog.Accepted:
            raise SystemExit(0)

        host, port, session, player_name = connect.connect_info()
        self._session = session

        self.engine = Engine()
        self.engine.running = True

        self.viewport = GameViewport(self.engine, self.client, self)
        self.setCentralWidget(self.viewport)

        try:
            self.client.connect(host, port, session, player_name)
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))
            raise SystemExit(1)

        scene_msg = self.client.wait_for("scene", timeout=5)
        if scene_msg is None:
            QMessageBox.critical(self, "Error", "Server did not send scene data")
            raise SystemExit(1)

        scene = scene_from_dict(scene_msg.data["data"])
        self.engine.set_scene(scene)

        self.setWindowTitle(f"Prima - {session} ({host}:{port})")

    def closeEvent(self, event):
        self.viewport.closeEvent(event)
        event.accept()


def main():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        font = QFont("Segoe UI", 9)
        app.setFont(font)
    try:
        window = GameWindow()
        window.show()
        sys.exit(app.exec_())
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
