from OpenGL import GL
from .math_utils import Vector3, Matrix4
from .objects import Part, Wedge, Cylinder, Sphere
import numpy as np
import math


VERTEX_SHADER_SRC = """
#version 330 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec3 a_color;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

out vec3 v_normal;
out vec3 v_frag_pos;
out vec3 v_color;

void main() {
    vec4 world_pos = u_model * vec4(a_position, 1.0);
    gl_Position = u_projection * u_view * world_pos;
    v_normal = mat3(transpose(inverse(u_model))) * a_normal;
    v_frag_pos = world_pos.xyz;
    v_color = a_color;
}
"""

FRAGMENT_SHADER_SRC = """
#version 330 core
in vec3 v_normal;
in vec3 v_frag_pos;
in vec3 v_color;

uniform vec3 u_ambient_color;
uniform float u_ambient_intensity;
uniform vec3 u_light_pos;
uniform vec3 u_light_color;
uniform float u_light_intensity;
uniform vec3 u_camera_pos;

out vec4 frag_color;

void main() {
    vec3 ambient = u_ambient_color * u_ambient_intensity * v_color;

    vec3 norm = normalize(v_normal);
    vec3 light_dir = normalize(u_light_pos - v_frag_pos);
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * u_light_color * u_light_intensity * v_color;

    vec3 view_dir = normalize(u_camera_pos - v_frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
    vec3 specular = spec * u_light_color * 0.3;

    frag_color = vec4(ambient + diffuse + specular, 1.0);
}
"""


def compile_shader(source, shader_type):
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
        log = GL.glGetShaderInfoLog(shader)
        GL.glDeleteShader(shader)
        raise RuntimeError(f"Shader compile error: {log}")
    return shader


def create_shader_program(vertex_src, fragment_src):
    vs = compile_shader(vertex_src, GL.GL_VERTEX_SHADER)
    fs = compile_shader(fragment_src, GL.GL_FRAGMENT_SHADER)
    program = GL.glCreateProgram()
    GL.glAttachShader(program, vs)
    GL.glAttachShader(program, fs)
    GL.glLinkProgram(program)
    if GL.glGetProgramiv(program, GL.GL_LINK_STATUS) != GL.GL_TRUE:
        log = GL.glGetProgramInfoLog(program)
        GL.glDeleteProgram(program)
        raise RuntimeError(f"Program link error: {log}")
    GL.glDeleteShader(vs)
    GL.glDeleteShader(fs)
    return program


_mesh_cache = {}


def _build_box(sw, sh, sd):
    w, h, d = sw / 2, sh / 2, sd / 2
    verts = np.array([
        [-w, -h, -d], [ w, -h, -d], [ w,  h, -d], [-w,  h, -d],
        [-w, -h,  d], [ w, -h,  d], [ w,  h,  d], [-w,  h,  d],
    ], dtype=np.float32)

    idx = np.array([
        4,5,6, 4,6,7,
        1,0,3, 1,3,2,
        3,7,6, 3,6,2,
        4,0,1, 4,1,5,
        5,1,2, 5,2,6,
        0,4,7, 0,7,3,
    ], dtype=np.uint32)

    norms = np.zeros((len(idx), 3), dtype=np.float32)
    for i in range(0, len(idx), 3):
        v0 = verts[idx[i]]
        v1 = verts[idx[i+1]]
        v2 = verts[idx[i+2]]
        n = np.cross(v1 - v0, v2 - v0)
        n = n / (np.linalg.norm(n) + 1e-8)
        norms[i] = norms[i+1] = norms[i+2] = n

    return verts, idx, norms


def _build_wedge(sw, sh, sd):
    w, h, d = sw / 2, sh / 2, sd / 2

    verts = np.array([
        [-w, -h, -d], [ w, -h, -d], [ 0,  h, -d],
        [-w, -h,  d], [ w, -h,  d], [ 0,  h,  d],
    ], dtype=np.float32)

    idx = np.array([
        0,2,1,
        3,4,5,
        0,1,4, 0,4,3,
        1,2,5, 1,5,4,
        0,3,2, 3,5,2,
    ], dtype=np.uint32)

    norms = np.zeros((len(idx), 3), dtype=np.float32)
    for i in range(0, len(idx), 3):
        v0 = verts[idx[i]]
        v1 = verts[idx[i+1]]
        v2 = verts[idx[i+2]]
        n = np.cross(v1 - v0, v2 - v0)
        ln = np.linalg.norm(n)
        if ln > 1e-8:
            n = n / ln
        norms[i] = norms[i+1] = norms[i+2] = n

    return verts, idx, norms


def _build_sphere(radius, segments=16):
    verts = []
    idx = []
    norms = []

    for lat in range(segments + 1):
        theta = lat * math.pi / segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        for lon in range(segments + 1):
            phi = lon * 2 * math.pi / segments
            x = radius * sin_theta * math.cos(phi)
            y = radius * cos_theta
            z = radius * sin_theta * math.sin(phi)
            verts.append([x, y, z])
            n = [x / radius, y / radius, z / radius]
            norms.append(n)

    for lat in range(segments):
        for lon in range(segments):
            first = lat * (segments + 1) + lon
            second = first + segments + 1
            idx.extend([first, second, first + 1])
            idx.extend([second, second + 1, first + 1])

    return np.array(verts, dtype=np.float32), np.array(idx, dtype=np.uint32), np.array(norms, dtype=np.float32)


def _build_cylinder(radius, height, segments=24):
    h = height / 2
    verts = []
    idx = []

    verts.append([0.0, -h, 0.0])
    for i in range(segments):
        a = 2 * math.pi * i / segments
        verts.append([radius * math.cos(a), -h, radius * math.sin(a)])

    top_start = len(verts)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        verts.append([radius * math.cos(a), h, radius * math.sin(a)])
    verts.append([0.0, h, 0.0])

    for i in range(segments):
        nxt = (i + 1) % segments
        idx.extend([0, i + 1, nxt + 1])

    for i in range(segments):
        nxt = (i + 1) % segments
        idx.extend([top_start + i, top_start + nxt, top_start + segments])

    for i in range(segments):
        nxt = (i + 1) % segments
        idx.extend([i + 1, top_start + i, nxt + 1])
        idx.extend([nxt + 1, top_start + i, top_start + nxt])

    verts = np.array(verts, dtype=np.float32)
    idx = np.array(idx, dtype=np.uint32)

    norms = np.zeros((len(idx), 3), dtype=np.float32)
    for i in range(0, len(idx), 3):
        v0 = verts[idx[i]]
        v1 = verts[idx[i+1]]
        v2 = verts[idx[i+2]]
        n = np.cross(v1 - v0, v2 - v0)
        ln = np.linalg.norm(n)
        if ln > 1e-8:
            n = n / ln
        norms[i] = norms[i+1] = norms[i+2] = n

    return verts, idx, norms


def get_box_mesh():
    key = "box"
    if key in _mesh_cache:
        return _mesh_cache[key]
    _mesh_cache[key] = _build_box(1, 1, 1)
    return _mesh_cache[key]


def get_wedge_mesh():
    key = "wedge"
    if key in _mesh_cache:
        return _mesh_cache[key]
    _mesh_cache[key] = _build_wedge(1, 1, 1)
    return _mesh_cache[key]


def get_sphere_mesh():
    key = "sphere"
    if key in _mesh_cache:
        return _mesh_cache[key]
    _mesh_cache[key] = _build_sphere(0.5)
    return _mesh_cache[key]


def get_cylinder_mesh():
    key = "cylinder"
    if key in _mesh_cache:
        return _mesh_cache[key]
    _mesh_cache[key] = _build_cylinder(0.5, 1)
    return _mesh_cache[key]


_mesh_map = {
    "Box": get_box_mesh,
    "Wedge": get_wedge_mesh,
    "Sphere": get_sphere_mesh,
    "Cylinder": get_cylinder_mesh,
}


class Renderer:
    def __init__(self):
        self.shader_program = None
        self.vaos = {}
        self.vbos = {}
        self.ebos = {}

        self._setup_shaders()
        self._setup_buffers()

    def _setup_shaders(self):
        self.shader_program = create_shader_program(VERTEX_SHADER_SRC, FRAGMENT_SHADER_SRC)

    def _setup_buffers(self):
        for name, builder in _mesh_map.items():
            verts, idx, norms = builder()
            vao = GL.glGenVertexArrays(1)
            vbo = GL.glGenBuffers(1)
            ebo = GL.glGenBuffers(1)
            nbo = GL.glGenBuffers(1)

            GL.glBindVertexArray(vao)

            positions = np.zeros((len(idx), 3), dtype=np.float32)
            for i, j in enumerate(idx):
                positions[i] = verts[j]

            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, positions.nbytes, positions, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
            GL.glEnableVertexAttribArray(0)

            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, nbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, norms.nbytes, norms, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
            GL.glEnableVertexAttribArray(1)

            colors = np.ones((len(idx), 3), dtype=np.float32) * 0.8
            cbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, cbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, colors.nbytes, colors, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
            GL.glEnableVertexAttribArray(2)

            GL.glBindVertexArray(0)

            self.vaos[name] = (vao, len(positions), cbo)

    def render(self, scene, view_matrix, proj_matrix, camera_pos):
        program = self.shader_program
        GL.glUseProgram(program)

        GL.glUniform3f(
            GL.glGetUniformLocation(program, "u_ambient_color"),
            *scene.ambient_color
        )
        GL.glUniform1f(
            GL.glGetUniformLocation(program, "u_ambient_intensity"),
            scene.ambient_intensity
        )
        GL.glUniform3f(
            GL.glGetUniformLocation(program, "u_camera_pos"),
            camera_pos.x, camera_pos.y, camera_pos.z
        )

        light_pos = Vector3(10, 20, 10)
        light_color = (1.0, 1.0, 1.0)
        light_intensity = 1.0

        objects = scene.get_all_objects()
        for obj in objects:
            if not obj.visible:
                continue

            shape = None
            if hasattr(obj, 'shape'):
                shape = obj.shape
            elif obj.object_type in _mesh_map:
                shape = obj.object_type
            else:
                continue

            if shape not in self.vaos:
                continue

            model = obj.get_world_matrix()
            vao, count, cbo = self.vaos[shape]

            GL.glUniformMatrix4fv(
                GL.glGetUniformLocation(program, "u_model"), 1, GL.GL_FALSE, model.data.T.flatten()
            )
            GL.glUniformMatrix4fv(
                GL.glGetUniformLocation(program, "u_view"), 1, GL.GL_FALSE, view_matrix.data.T.flatten()
            )
            GL.glUniformMatrix4fv(
                GL.glGetUniformLocation(program, "u_projection"), 1, GL.GL_FALSE, proj_matrix.data.T.flatten()
            )
            GL.glUniform3f(
                GL.glGetUniformLocation(program, "u_light_pos"),
                light_pos.x, light_pos.y, light_pos.z
            )
            GL.glUniform3f(
                GL.glGetUniformLocation(program, "u_light_color"),
                *light_color
            )
            GL.glUniform1f(
                GL.glGetUniformLocation(program, "u_light_intensity"),
                light_intensity
            )

            mat = getattr(obj, 'material', None)
            if mat:
                c = mat.color
                r, g, b = c.red() / 255, c.green() / 255, c.blue() / 255
                colors_arr = np.full((count, 3), [r, g, b], dtype=np.float32)
                GL.glBindBuffer(GL.GL_ARRAY_BUFFER, cbo)
                GL.glBufferData(GL.GL_ARRAY_BUFFER, colors_arr.nbytes, colors_arr, GL.GL_DYNAMIC_DRAW)

            GL.glBindVertexArray(vao)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, count)
            GL.glBindVertexArray(0)

        GL.glUseProgram(0)

    def destroy(self):
        GL.glDeleteProgram(self.shader_program)
        for name, (vao, count, cbo) in self.vaos.items():
            GL.glDeleteVertexArrays(1, [vao])
