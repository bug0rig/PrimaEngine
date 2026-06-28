from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import (
    QMouseEvent, QKeyEvent, QPainter, QColor, QFont,
)
from OpenGL import GL
from prima.engine.camera import build_view_matrix, build_projection_matrix
from prima.engine.math_utils import Vector3, Matrix4
from prima.engine.rendering import create_shader_program
from .gizmo import Gizmo
import math
import numpy as np


class Viewport3D(QOpenGLWidget):
    object_selected = pyqtSignal(object)
    orbited = pyqtSignal()

    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setMinimumSize(400, 300)
        self.setFocusPolicy(Qt.StrongFocus)

        self.cam_position = Vector3(8, 6, 8)
        self.cam_rotation = Vector3(math.radians(-25), math.radians(-135), 0)
        self.cam_fov = 70.0
        self.cam_near = 0.01
        self.cam_far = 1000.0

        self._last_mouse = None
        self._panning = False
        self._orbiting = False
        self._orbit_detected = False
        self._zoom_speed = 0.005
        self._orbit_speed = 0.005
        self._pan_speed = 0.02
        self.move_speed = 8.0
        self.keys = set()

        self.selected_object = None
        self.grid_size = 10
        self.grid_div = 10
        self.show_grid = True
        self.show_debug = False
        self.gizmo = Gizmo()
        self.gizmo_mode = "translate"

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)

    def paintGL(self):
        self.engine.update()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        aspect = self.width() / max(self.height(), 1)
        view = build_view_matrix(self.cam_position, self.cam_rotation)
        proj = build_projection_matrix(self.cam_fov, aspect, self.cam_near, self.cam_far)

        self.engine.render(view, proj, self.cam_position)

        if self.show_grid:
            self._render_grid(view, proj)

        if self.selected_object:
            self._render_selection(view, proj)

        if self.selected_object and hasattr(self, '_line_shader'):
            self.gizmo.render(
                self._line_shader,
                self.selected_object.get_world_position(),
                view, proj,
                self.width(), self.height(),
            )

        if self.show_debug:
            self._render_debug_overlay()

    def _build_grid_vao(self):
        half = self.grid_size / 2
        step = self.grid_size / self.grid_div
        lines = []
        for i in range(self.grid_div + 1):
            pos = -half + i * step
            lines.extend([(pos, -0.01, -half), (pos, -0.01, half)])
            lines.extend([(-half, -0.01, pos), (half, -0.01, pos)])
        lines.extend([(-half, -0.01, 0), (half, -0.01, 0)])
        lines.extend([(0, -0.01, -half), (0, -0.01, half)])

        verts = np.array(lines, dtype=np.float32)
        self._grid_count = len(lines)

        vao = GL.glGenVertexArrays(1)
        vbo = GL.glGenBuffers(1)
        GL.glBindVertexArray(vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, verts.nbytes, verts, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        GL.glBindVertexArray(0)
        self._grid_vao = vao

    def _build_line_shader(self):
        vs = """
        #version 330 core
        layout(location = 0) in vec3 a_pos;
        uniform mat4 u_mvp;
        void main() {
            gl_Position = u_mvp * vec4(a_pos, 1.0);
        }
        """
        fs = """
        #version 330 core
        uniform vec3 u_color;
        out vec4 frag_color;
        void main() {
            frag_color = vec4(u_color, 1.0);
        }
        """
        self._line_shader = create_shader_program(vs, fs)

    def initializeGL(self):
        GL.glClearColor(0.15, 0.15, 0.18, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        self.engine.initialize()
        self._build_line_shader()
        self._build_grid_vao()

    def _render_grid(self, view, proj):
        if not hasattr(self, '_grid_vao'):
            return
        mvp = proj * view
        program = self._line_shader
        GL.glUseProgram(program)
        GL.glUniformMatrix4fv(
            GL.glGetUniformLocation(program, "u_mvp"), 1, GL.GL_FALSE, mvp.data.T.flatten()
        )
        GL.glUniform3f(GL.glGetUniformLocation(program, "u_color"), 0.3, 0.3, 0.35)
        GL.glBindVertexArray(self._grid_vao)
        GL.glDrawArrays(GL.GL_LINES, 0, self._grid_count)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def _render_selection(self, view, proj):
        obj = self.selected_object
        if not obj or not hasattr(self, '_line_shader'):
            return
        model = obj.get_world_matrix()
        mvp = proj * view * model
        program = self._line_shader
        GL.glUseProgram(program)
        GL.glUniformMatrix4fv(
            GL.glGetUniformLocation(program, "u_mvp"), 1, GL.GL_FALSE, mvp.data.T.flatten()
        )
        GL.glUniform3f(GL.glGetUniformLocation(program, "u_color"), 1.0, 0.8, 0.0)

        box_verts = np.array([
            -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5,  0.5, -0.5, -0.5,  0.5, -0.5,
            -0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  0.5,  0.5,
        ], dtype=np.float32)
        box_idx = np.array([
            0,1,1,2,2,3,3,0, 4,5,5,6,6,7,7,4, 0,4,1,5,2,6,3,7
        ], dtype=np.uint32)

        vao = GL.glGenVertexArrays(1)
        vbo = GL.glGenBuffers(1)
        ebo = GL.glGenBuffers(1)
        GL.glBindVertexArray(vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, box_verts.nbytes, box_verts, GL.GL_STREAM_DRAW)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, box_idx.nbytes, box_idx, GL.GL_STREAM_DRAW)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(vao)
        GL.glDrawElements(GL.GL_LINES, len(box_idx), GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)

        GL.glDeleteVertexArrays(1, [vao])
        GL.glDeleteBuffers(1, [vbo])
        GL.glDeleteBuffers(1, [ebo])
        GL.glUseProgram(0)

    def _render_debug_overlay(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont("Consolas, monospace", 11)
        font.setStyleHint(QFont.Monospace)
        painter.setFont(font)

        lines = []
        engine = self.engine

        lines.append(f"FPS: {engine.fps:.0f}")
        lines.append(f"Delta: {engine.delta_time*1000:.1f} ms")

        obj_count = len(engine.scene.get_all_objects())
        lines.append(f"Objects: {obj_count}")

        body_count = len(engine.physics._body_map) if engine.physics else 0
        lines.append(f"Bodies: {body_count}")

        contact_count = len(engine.physics._world.contacts) if hasattr(engine.physics, '_world') else 0
        lines.append(f"Contacts: {contact_count}")

        gizmo_mode_map = {"translate": "1", "rotate": "2", "scale": "3"}
        snap_label = f" [SNAP={self.gizmo.snap_value}]" if self.gizmo.snap_enabled else ""
        csnap_label = " [V-SNAP]" if self.gizmo.connector_snap_enabled else ""
        lines.append(f"Gizmo: [{gizmo_mode_map.get(self.gizmo.mode, '?')}] {self.gizmo.mode.upper()}{snap_label}{csnap_label}")

        if engine.running:
            lines.append(f"Physics: RUNNING")
        else:
            lines.append(f"Physics: PAUSED (editor)")

        sel = self.selected_object
        if sel:
            lines.append(f"")
            lines.append(f"Selected: {sel.name} ({sel.object_type})")
            lines.append(f"  Pos: {sel.position.x:.2f}, {sel.position.y:.2f}, {sel.position.z:.2f}")
            if hasattr(sel, 'mass'):
                lines.append(f"  Mass: {sel.mass:.2f}")
            if hasattr(sel, 'physics_material'):
                lines.append(f"  Material: {sel.physics_material}")
            if hasattr(sel, 'anchored'):
                lines.append(f"  Anchored: {sel.anchored}")

        line_h = 20
        x, y = 12, line_h
        bg = QColor(0, 0, 0, 160)
        fg = QColor(220, 220, 220)

        painter.fillRect(0, 0, 320, len(lines) * line_h + 6, bg)

        painter.setPen(fg)
        for line in lines:
            painter.drawText(x, y, line)
            y += line_h

        painter.end()

    def _tick(self):
        self._update_freecam()
        self.update()

    def _update_freecam(self):
        cos_p = math.cos(self.cam_rotation.x)
        forward = Vector3(
            math.sin(self.cam_rotation.y) * cos_p,
            math.sin(self.cam_rotation.x),
            math.cos(self.cam_rotation.y) * cos_p
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

    def keyPressEvent(self, event: QKeyEvent):
        self.keys.add(event.key())
        if event.key() == Qt.Key_F3:
            self.show_debug = not self.show_debug
            self.update()
        elif event.key() == Qt.Key_1:
            self.gizmo.mode = "translate"
            self.update()
        elif event.key() == Qt.Key_2:
            self.gizmo.mode = "rotate"
            self.update()
        elif event.key() == Qt.Key_3:
            self.gizmo.mode = "scale"
            self.update()
        elif event.key() == Qt.Key_V and not self.gizmo.is_dragging:
            self.gizmo.connector_snap_enabled = not self.gizmo.connector_snap_enabled
            self.update()
        elif event.key() == Qt.Key_Delete and self.selected_object:
            self._delete_selected()
        elif event.key() == Qt.Key_D and event.modifiers() & Qt.ControlModifier and self.selected_object:
            self._duplicate_selected()

    def keyReleaseEvent(self, event: QKeyEvent):
        self.keys.discard(event.key())

    def focusOutEvent(self, event):
        self.keys.clear()
        super().focusOutEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        self._last_mouse = (event.x(), event.y())
        if event.button() == Qt.LeftButton and self.selected_object:
            aspect = self.width() / max(self.height(), 1)
            view = build_view_matrix(self.cam_position, self.cam_rotation)
            proj = build_projection_matrix(self.cam_fov, aspect, self.cam_near, self.cam_far)
            hit = self.gizmo.hit_test(
                event.x(), event.y(),
                self.selected_object.get_world_position(),
                view, proj, self.width(), self.height(),
            )
            if hit:
                self.gizmo.start_drag(hit, (event.x(), event.y()), self.selected_object.position, view, proj, self.width(), self.height())
                return

        if event.button() == Qt.MiddleButton:
            self._panning = True
        elif event.button() == Qt.RightButton:
            self._orbiting = True
        elif event.button() == Qt.LeftButton:
            self._select_object(event.x(), event.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.gizmo.is_dragging:
            self.gizmo.end_drag()
        if event.button() == Qt.MiddleButton:
            self._panning = False
        elif event.button() == Qt.RightButton:
            self._orbiting = False
            self._orbit_detected = False
        self._last_mouse = None

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.gizmo.is_dragging and self.selected_object:
            self.gizmo.snap_value = 0.05 if Qt.Key_Control in self.keys else 0.25
            aspect = self.width() / max(self.height(), 1)
            view = build_view_matrix(self.cam_position, self.cam_rotation)
            proj = build_projection_matrix(self.cam_fov, aspect, self.cam_near, self.cam_far)
            new_pos = self.gizmo.update_drag(
                (event.x(), event.y()),
                self.selected_object.position,
                view, proj, self.width(), self.height(),
                self.cam_position,
            )
            if new_pos is not None and self.gizmo.connector_snap_enabled:
                new_pos = self._apply_connector_snap(new_pos)
            if new_pos is not None:
                self.selected_object.position = new_pos
            return

        if self._last_mouse is None:
            return
        dx = event.x() - self._last_mouse[0]
        dy = event.y() - self._last_mouse[1]
        self._last_mouse = (event.x(), event.y())

        if self.selected_object:
            aspect = self.width() / max(self.height(), 1)
            view = build_view_matrix(self.cam_position, self.cam_rotation)
            proj = build_projection_matrix(self.cam_fov, aspect, self.cam_near, self.cam_far)
            hit = self.gizmo.hit_test(
                event.x(), event.y(),
                self.selected_object.get_world_position(),
                view, proj, self.width(), self.height(),
            )
            self.gizmo.hovered_axis = hit

        if self._orbiting:
            self.cam_rotation.y -= dx * self._orbit_speed
            self.cam_rotation.x -= dy * self._orbit_speed
            self.cam_rotation.x = max(-math.pi / 2, min(math.pi / 2, self.cam_rotation.x))
            if not self._orbit_detected:
                self._orbit_detected = True
                self.orbited.emit()
        elif self._panning:
            forward = Vector3(
                math.sin(self.cam_rotation.y),
                0,
                math.cos(self.cam_rotation.y)
            ).normalized()
            right = Vector3(
                -math.cos(self.cam_rotation.y),
                0,
                math.sin(self.cam_rotation.y)
            ).normalized()
            self.cam_position = self.cam_position + right * (dx * self._pan_speed)
            self.cam_position = self.cam_position + forward * (dy * self._pan_speed)

    def wheelEvent(self, event):
        forward = Vector3(
            math.sin(self.cam_rotation.y) * math.cos(self.cam_rotation.x),
            math.sin(self.cam_rotation.x),
            math.cos(self.cam_rotation.y) * math.cos(self.cam_rotation.x)
        ).normalized()
        self.cam_position = self.cam_position + forward * (-event.angleDelta().y() * self._zoom_speed)

    def _apply_connector_snap(self, candidate_pos):
        obj = self.selected_object
        if not obj or not obj.connectors:
            return candidate_pos
        best = None
        best_dist = self.gizmo.connector_snap_distance
        for conn_a in obj.connectors:
            wa = candidate_pos + conn_a.position
            for other in self.engine.scene.get_all_objects():
                if other is obj or other.object_type == "Root":
                    continue
                for conn_b in other.connectors:
                    wb = other.get_world_position() + conn_b.position
                    d = (wa - wb).length()
                    if d < best_dist:
                        best_dist = d
                        best = wb - wa
        if best is not None:
            return candidate_pos + best
        return candidate_pos

    def _select_object(self, x, y):
        objs = self.engine.scene.get_all_objects()
        if not objs:
            return

        best = None
        best_dist = float('inf')

        aspect = self.width() / max(self.height(), 1)
        view = build_view_matrix(self.cam_position, self.cam_rotation)
        proj = build_projection_matrix(self.cam_fov, aspect, self.cam_near, self.cam_far).data

        ndc_x = (2.0 * x) / self.width() - 1.0
        ndc_y = 1.0 - (2.0 * y) / self.height()

        for obj in objs:
            if obj.object_type in ("Root", "Camera", "Light", "Script"):
                continue
            wp = obj.get_world_position()
            clip = proj @ (view * obj.get_world_matrix()).data @ [0, 0, 0, 1]
            if abs(clip[3]) < 1e-8:
                continue
            sx = clip[0] / clip[3]
            sy = clip[1] / clip[3]
            dist = math.sqrt((sx - ndc_x) ** 2 + (sy - ndc_y) ** 2)
            if dist < best_dist:
                best_dist = dist
                best = obj

        if best_dist < 0.15:
            self.selected_object = best
            self.object_selected.emit(best)
        else:
            self.selected_object = None
            self.object_selected.emit(None)

    def focus_on(self, obj):
        if obj is None:
            return
        wp = obj.get_world_position()
        self.cam_position = wp + Vector3(5, 3, 5)
        self.cam_rotation = Vector3(math.radians(-25), math.radians(-135), 0)

    def reset_camera(self):
        self.cam_position = Vector3(8, 6, 8)
        self.cam_rotation = Vector3(math.radians(-25), math.radians(-135), 0)

    def _delete_selected(self):
        obj = self.selected_object
        if obj and obj.object_type != "Root":
            self.engine.scene.remove_object(obj)
            self.selected_object = None
            self.object_selected.emit(None)

    def _duplicate_selected(self):
        obj = self.selected_object
        if obj:
            dup = obj.duplicate()
            parent = obj.parent or self.engine.scene.root
            parent.add_child(dup)
            self.selected_object = dup
            self.object_selected.emit(dup)
