from PyQt5.QtWidgets import QMainWindow, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from OpenGL import GL
from prima.engine.camera import build_view_matrix, build_projection_matrix
from prima.engine.math_utils import Vector3, Matrix4
from prima.engine.core import Engine
from prima.engine.scene import SceneObject
import math


PLAYER_HEIGHT = 5.5
PLAYER_RADIUS = 1.0
PLAYER_EYE = 2.5
PLAYER_SPEED = 5.0
JUMP_SPEED = 6.0


class RuntimeViewport(QOpenGLWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        self.player = None
        self.move_speed = PLAYER_SPEED
        self.mouse_sensitivity = 0.003
        self.keys = set()
        self._mouse_captured = False
        self._last_mx = 0
        self._last_my = 0
        self._cam_rot = Vector3(math.radians(-10), 0, 0)
        self._cam_distance = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(16)

    def _spawn_player(self):
        p = SceneObject("Player")
        p.object_type = "Player"
        p.size = Vector3(1, 1, 1)
        p.collision_height = PLAYER_HEIGHT
        p.position = Vector3(0, PLAYER_HEIGHT / 2 + 0.5, 0)
        p.anchored = False
        p.mass = 70.0
        p.velocity = Vector3.zero()
        p.visible = False
        p.color = (0.2, 0.6, 1.0)
        self.engine.scene.root.add_child(p)
        self.player = p

        # Build capsule visual from primitives
        cyl = SceneObject("PlayerBody")
        cyl.object_type = "Part"
        cyl.shape = "Cylinder"
        cyl.size = Vector3(PLAYER_RADIUS * 2, PLAYER_HEIGHT - PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        cyl.position = Vector3(0, 0, 0)
        cyl.color = (0.2, 0.6, 1.0)
        cyl.material.set_color(51, 153, 255)
        p.add_child(cyl)

        top = SceneObject("PlayerHead")
        top.object_type = "Part"
        top.shape = "Sphere"
        top.size = Vector3(PLAYER_RADIUS * 2, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        top.position = Vector3(0, PLAYER_HEIGHT / 2 - PLAYER_RADIUS, 0)
        top.color = (0.2, 0.6, 1.0)
        top.material.set_color(51, 153, 255)
        p.add_child(top)

        bot = SceneObject("PlayerFeet")
        bot.object_type = "Part"
        bot.shape = "Sphere"
        bot.size = Vector3(PLAYER_RADIUS * 2, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        bot.position = Vector3(0, -PLAYER_HEIGHT / 2 + PLAYER_RADIUS, 0)
        bot.color = (0.2, 0.6, 1.0)
        bot.material.set_color(51, 153, 255)
        p.add_child(bot)

    def initializeGL(self):
        GL.glClearColor(0.15, 0.15, 0.18, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        self.engine.initialize()
        self._spawn_player()

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)

    def paintGL(self):
        self.engine.update()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        aspect = self.width() / max(self.height(), 1)

        pp = self.player.position if self.player else Vector3(0, 0, 0)
        pitch = self._cam_rot.x
        yaw = self._cam_rot.y
        cos_p = math.cos(pitch)
        sin_p = math.sin(pitch)
        cos_y = math.cos(yaw)
        sin_y = math.sin(yaw)
        eye_base = Vector3(pp.x, pp.y + PLAYER_EYE, pp.z)
        offset = Vector3(
            -sin_y * cos_p * self._cam_distance,
            sin_p * self._cam_distance,
            -cos_y * cos_p * self._cam_distance,
        )
        eye = eye_base + offset
        if self._cam_distance < 0.5:
            view = build_view_matrix(eye, self._cam_rot)
        else:
            target = pp + Vector3(0, PLAYER_EYE * 0.4, 0)
            view = Matrix4.look_at(eye, target, Vector3.up())
        proj = build_projection_matrix(70, aspect, 0.01, 1000)
        self.engine.render(view, proj, eye)

    def _update(self):
        if self.player is None:
            return
        forward = Vector3(
            math.sin(self._cam_rot.y), 0, math.cos(self._cam_rot.y)
        ).normalized()
        right = Vector3(
            -math.cos(self._cam_rot.y), 0, math.sin(self._cam_rot.y)
        ).normalized()

        vx, vz = 0.0, 0.0
        if Qt.Key_W in self.keys:
            vx += forward.x; vz += forward.z
        if Qt.Key_S in self.keys:
            vx -= forward.x; vz -= forward.z
        if Qt.Key_A in self.keys:
            vx -= right.x; vz -= right.z
        if Qt.Key_D in self.keys:
            vx += right.x; vz += right.z

        vel = self.player.velocity
        h_speed = math.sqrt(vx * vx + vz * vz)
        if h_speed > 0:
            vx /= h_speed; vz /= h_speed
            vel.x = vx * self.move_speed
            vel.z = vz * self.move_speed
        else:
            # friction — stop horizontal
            vel.x *= 0.85
            vel.z *= 0.85
            if abs(vel.x) < 0.01: vel.x = 0.0
            if abs(vel.z) < 0.01: vel.z = 0.0

        if Qt.Key_Space in self.keys:
            vel.y = JUMP_SPEED

        self.player.velocity = vel
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
            try:
                self.grabMouse()
            except:
                pass

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton and self._mouse_captured:
            self._mouse_captured = False
            self.setCursor(Qt.ArrowCursor)
            try:
                self.releaseMouse()
            except:
                pass

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._mouse_captured:
            return
        dx = event.x() - self._last_mx
        dy = event.y() - self._last_my
        if dx == 0 and dy == 0:
            return
        self._last_mx = event.x()
        self._last_my = event.y()

        self._cam_rot.y -= dx * self.mouse_sensitivity  # NEVER TOUCH — correct for this coord system
        self._cam_rot.x -= dy * self.mouse_sensitivity
        self._cam_rot.x = max(-math.pi / 2 + 0.01, min(math.pi / 2 - 0.01, self._cam_rot.x))

    def wheelEvent(self, event: QWheelEvent):
        self._cam_distance -= event.angleDelta().y() * 0.005
        self._cam_distance = max(0.0, min(50.0, self._cam_distance))
        self.update()

    def closeEvent(self, event):
        self._timer.stop()
        self.engine.shutdown()
        event.accept()


class RuntimeWindow(QMainWindow):
    def __init__(self, scene):
        super().__init__()
        self.setWindowTitle("Prima - Runtime (WASD move, RClick look, Scroll zoom, Space jump, Esc exit)")
        self.setMinimumSize(800, 600)

        self.engine = Engine()
        self.engine.running = True
        self.engine.set_scene(scene)

        self.viewport = RuntimeViewport(self.engine, self)
        self.setCentralWidget(self.viewport)

    def closeEvent(self, event):
        self.viewport.closeEvent(event)
        event.accept()
