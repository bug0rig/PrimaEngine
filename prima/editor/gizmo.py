"""3D transform gizmo — translate/rotate/scale handles for the viewport."""

import math
import numpy as np
from OpenGL import GL
from prima.engine.math_utils import Vector3


AXIS_COLORS = {
    "x": (1.0, 0.2, 0.2),
    "y": (0.2, 1.0, 0.2),
    "z": (0.2, 0.5, 1.0),
}
AXIS_VECTORS = {
    "x": Vector3(1, 0, 0),
    "y": Vector3(0, 1, 0),
    "z": Vector3(0, 0, 1),
}
AXIS_ORDER = ("x", "y", "z")

HOVER_BRIGHTNESS = 1.5
HIT_THRESHOLD_PX = 12
ARROW_LENGTH = 0.3
ARROW_RADIUS = 0.04
ARROW_SEGMENTS = 16
SHAFT_LENGTH = 0.7
PIXEL_SIZE = 120.0


def _world_to_screen(world_pos, view, proj, viewport_w, viewport_h):
    clip = proj.data @ (view.data @ [world_pos.x, world_pos.y, world_pos.z, 1.0])
    if abs(clip[3]) < 1e-10:
        return None
    ndc = clip[0] / clip[3], clip[1] / clip[3]
    sx = (ndc[0] + 1.0) * 0.5 * viewport_w
    sy = (1.0 - ndc[1]) * 0.5 * viewport_h
    if clip[3] < 0:
        return None
    return sx, sy


def _screen_ray(mx, my, view, proj, viewport_w, viewport_h):
    ndc_x = (2.0 * mx) / viewport_w - 1.0
    ndc_y = 1.0 - (2.0 * my) / viewport_h
    inv_proj = proj.inverse()
    inv_view = view.inverse()
    near_clip = inv_proj.data @ [ndc_x, ndc_y, -1.0, 1.0]
    far_clip = inv_proj.data @ [ndc_x, ndc_y, 1.0, 1.0]
    near_world = inv_view.data @ (near_clip / near_clip[3])
    far_world = inv_view.data @ (far_clip / far_clip[3])
    origin = Vector3(near_world[0], near_world[1], near_world[2])
    direction = Vector3(
        far_world[0] - origin.x,
        far_world[1] - origin.y,
        far_world[2] - origin.z,
    ).normalized()
    return origin, direction


def _closest_point_on_line(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    dot = apx * abx + apy * aby
    len_sq = abx * abx + aby * aby
    t = dot / max(len_sq, 1e-10)
    t = max(0, min(1, t))
    return (ax + abx * t, ay + aby * t)


def _axis_rotation(dir_vec):
    z = Vector3(dir_vec.x, dir_vec.y, dir_vec.z).normalized()
    ref = Vector3(0, 1, 0)
    if abs(z.dot(ref)) > 0.99:
        ref = Vector3(1, 0, 0)
    x = ref.cross(z).normalized()
    y = z.cross(x).normalized()
    return x, y, z


def _compute_gizmo_scale(obj_pos, view, proj, viewport_w, viewport_h):
    screen = _world_to_screen(obj_pos, view, proj, viewport_w, viewport_h)
    if screen is None:
        return 1.0
    offset = obj_pos + AXIS_VECTORS["x"]
    offset_screen = _world_to_screen(offset, view, proj, viewport_w, viewport_h)
    if offset_screen is None:
        return 1.0
    ppu = max(abs(offset_screen[0] - screen[0]), abs(offset_screen[1] - screen[1]))
    if ppu < 1e-6:
        return 1.0
    return PIXEL_SIZE / ppu


def _axis_param(P0, O, D, A):
    """Return s such that L(s)=P0+s*A is closest to ray O+t*D."""
    op = P0 - O
    AD = A.dot(D)
    opD = op.dot(D)
    opA = op.dot(A)
    denom = 1.0 - AD * AD
    if abs(denom) < 1e-8:
        return 0.0
    t = (opD - opA * AD) / denom
    return t * AD - opA


class Gizmo:
    def __init__(self):
        self.mode = "translate"
        self.hovered_axis = None
        self.active_axis = None
        self.is_dragging = False
        self._drag_start_mouse = None
        self._drag_start_pos = None
        self._drag_axis_vec = None
        self._drag_start_s = None

        self.snap_enabled = True
        self.snap_value = 0.25
        self.connector_snap_enabled = False
        self.connector_snap_distance = 0.3

        self._built = False
        self._line_vao = None
        self._line_vbo = None
        self._arrow_vaos = {}
        self._arrow_idx_count = 0

    def _build_meshes(self):
        segs = ARROW_SEGMENTS
        verts = []
        idx = []

        # cone base cap (fan)
        center_idx = len(verts)
        verts.append((0.0, 0.0, 0.0))
        for i in range(segs):
            a = 2.0 * math.pi * i / segs
            verts.append((ARROW_RADIUS * math.cos(a), ARROW_RADIUS * math.sin(a), 0.0))
            n2 = (i + 1) % segs + 1
            idx.extend([center_idx, i + 1, n2])

        # cone tip
        tip_idx = len(verts)
        verts.append((0.0, 0.0, ARROW_LENGTH))
        for i in range(segs):
            n = i + 1
            n2 = (i + 1) % segs + 1
            idx.extend([tip_idx, n2, n])

        verts_arr = np.array(verts, dtype=np.float32)
        idx_arr = np.array(idx, dtype=np.uint32)
        self._arrow_idx_count = len(idx_arr)

        for axis in AXIS_ORDER:
            vao = GL.glGenVertexArrays(1)
            vbo = GL.glGenBuffers(1)
            ebo = GL.glGenBuffers(1)
            GL.glBindVertexArray(vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, verts_arr.nbytes, verts_arr, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
            GL.glEnableVertexAttribArray(0)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, idx_arr.nbytes, idx_arr, GL.GL_STATIC_DRAW)
            GL.glBindVertexArray(0)
            self._arrow_vaos[axis] = vao

        # line VAO (reused for all axes)
        self._line_vao = GL.glGenVertexArrays(1)
        self._line_vbo = GL.glGenBuffers(1)
        GL.glBindVertexArray(self._line_vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._line_vbo)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        GL.glBindVertexArray(0)

        self._built = True

    def hit_test(self, mx, my, obj_pos, view, proj, viewport_w, viewport_h):
        if obj_pos is None:
            return None
        scale = _compute_gizmo_scale(obj_pos, view, proj, viewport_w, viewport_h)

        a_screen = _world_to_screen(obj_pos, view, proj, viewport_w, viewport_h)
        if a_screen is None:
            return None

        best_axis = None
        best_dist = HIT_THRESHOLD_PX * HIT_THRESHOLD_PX

        for axis in AXIS_ORDER:
            end = obj_pos + AXIS_VECTORS[axis] * scale
            b_screen = _world_to_screen(end, view, proj, viewport_w, viewport_h)
            if b_screen is None:
                continue
            cx, cy = _closest_point_on_line(mx, my, a_screen[0], a_screen[1], b_screen[0], b_screen[1])
            dx, dy = mx - cx, my - cy
            dist = dx * dx + dy * dy
            if dist < best_dist:
                best_dist = dist
                best_axis = axis

        return best_axis

    def start_drag(self, axis, mouse_pos, obj_pos, view, proj, viewport_w, viewport_h):
        self.active_axis = axis
        self.is_dragging = True
        self._drag_start_mouse = mouse_pos
        self._drag_start_pos = Vector3(obj_pos.x, obj_pos.y, obj_pos.z)
        self._drag_axis_vec = AXIS_VECTORS[axis]

        origin, ray_dir = _screen_ray(
            mouse_pos[0], mouse_pos[1], view, proj, viewport_w, viewport_h
        )
        self._drag_start_s = _axis_param(self._drag_start_pos, origin, ray_dir, self._drag_axis_vec)

    def update_drag(self, mouse_pos, obj_pos, view, proj, viewport_w, viewport_h, cam_pos):
        if not self.is_dragging or self.active_axis is None:
            return None

        origin, ray_dir = _screen_ray(
            mouse_pos[0], mouse_pos[1], view, proj, viewport_w, viewport_h
        )

        s = _axis_param(self._drag_start_pos, origin, ray_dir, self._drag_axis_vec)
        delta = s - self._drag_start_s

        if self.snap_enabled:
            snap = self.snap_value
            delta = round(delta / snap) * snap

        return self._drag_start_pos + self._drag_axis_vec * delta

    def end_drag(self):
        self.active_axis = None
        self.is_dragging = False
        self._drag_start_mouse = None
        self._drag_start_pos = None
        self._drag_axis_vec = None
        self._drag_start_s = None

    def render(self, program, obj_pos, view, proj, viewport_w, viewport_h):
        if obj_pos is None:
            return
        if not self._built:
            self._build_meshes()

        scale = _compute_gizmo_scale(obj_pos, view, proj, viewport_w, viewport_h)

        mvp = proj.data @ view.data
        mvp_flat = mvp.T.flatten()

        GL.glUseProgram(program)
        GL.glDisable(GL.GL_DEPTH_TEST)

        for axis in AXIS_ORDER:
            r, g, b = AXIS_COLORS[axis]
            if (self.is_dragging and self.active_axis == axis) or (self.hovered_axis == axis and not self.is_dragging):
                r = min(r * HOVER_BRIGHTNESS, 1.0)
                g = min(g * HOVER_BRIGHTNESS, 1.0)
                b = min(b * HOVER_BRIGHTNESS, 1.0)

            GL.glUniform3f(GL.glGetUniformLocation(program, "u_color"), r, g, b)

            end = obj_pos + AXIS_VECTORS[axis] * scale

            # draw shaft line
            line_verts = np.array([
                [obj_pos.x, obj_pos.y, obj_pos.z],
                [end.x, end.y, end.z],
            ], dtype=np.float32)
            GL.glBindVertexArray(self._line_vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._line_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, line_verts.nbytes, line_verts, GL.GL_STREAM_DRAW)
            GL.glUniformMatrix4fv(GL.glGetUniformLocation(program, "u_mvp"), 1, GL.GL_FALSE, mvp_flat)
            GL.glDrawArrays(GL.GL_LINES, 0, 2)

            # draw arrow cone at end
            x, y, z = _axis_rotation(AXIS_VECTORS[axis])
            model = np.identity(4, dtype=np.float32)
            model[0, 0] = x.x; model[1, 0] = x.y; model[2, 0] = x.z
            model[0, 1] = y.x; model[1, 1] = y.y; model[2, 1] = y.z
            model[0, 2] = z.x; model[1, 2] = z.y; model[2, 2] = z.z
            model[0, 3] = end.x; model[1, 3] = end.y; model[2, 3] = end.z

            mvp_arrow = proj.data @ view.data @ model
            GL.glUniformMatrix4fv(GL.glGetUniformLocation(program, "u_mvp"), 1, GL.GL_FALSE, mvp_arrow.T.flatten())
            GL.glBindVertexArray(self._arrow_vaos[axis])
            GL.glDrawElements(GL.GL_TRIANGLES, self._arrow_idx_count, GL.GL_UNSIGNED_INT, None)

        GL.glBindVertexArray(0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glUseProgram(0)
