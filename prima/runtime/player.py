from PyQt5.QtWidgets import QMainWindow, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent, QMouseEvent
from OpenGL import GL
from prima.engine.camera import build_view_matrix, build_projection_matrix
from prima.engine.math_utils import Vector3
from prima.engine.core import Engine
import math


class RuntimeViewport(QOpenGLWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
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
        self._timer.timeout.connect(self._update)
        self._timer.start(16)

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

    def _update(self):
        forward = Vector3(
            math.sin(self.cam_rotation.y), 0, math.cos(self.cam_rotation.y)
        ).normalized()
        right = Vector3(
            -math.cos(self.cam_rotation.y), 0, math.sin(self.cam_rotation.y)
        ).normalized()

        speed = self.move_speed * self.engine.delta_time
        if Qt.Key_W in self.keys:
            self.cam_position = self.cam_position + forward * speed
        if Qt.Key_S in self.keys:
            self.cam_position = self.cam_position - forward * speed
        if Qt.Key_A in self.keys:
            self.cam_position = self.cam_position - right * speed
        if Qt.Key_D in self.keys:
            self.cam_position = self.cam_position + right * speed
        if Qt.Key_Space in self.keys:
            self.cam_position.y += speed
        if Qt.Key_Shift in self.keys:
            self.cam_position.y -= speed

        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        self.keys.add(event.key())
        if event.key() == Qt.Key_Escape:
            if self._mouse_captured:
                self._mouse_captured = False
                self.setCursor(Qt.ArrowCursor)
                self.releaseMouse()
            else:
                self.window().close()

    def keyReleaseEvent(self, event: QKeyEvent):
        self.keys.discard(event.key())

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

    def closeEvent(self, event):
        self._timer.stop()
        self.engine.shutdown()
        event.accept()


class RuntimeWindow(QMainWindow):
    def __init__(self, scene):
        super().__init__()
        self.setWindowTitle("Prima - Runtime (WASD move, Mouse look, Esc exit)")
        self.setMinimumSize(800, 600)

        self.engine = Engine()
        self.engine.running = True
        self.engine.set_scene(scene)

        self.viewport = RuntimeViewport(self.engine, self)
        self.setCentralWidget(self.viewport)

    def closeEvent(self, event):
        self.viewport.closeEvent(event)
        event.accept()
