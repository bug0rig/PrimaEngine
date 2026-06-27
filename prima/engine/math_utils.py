try:
    from ._math_utils import Vector3, Matrix4
except ImportError:
    import math
    import numpy as np

    class Vector3:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)

        def __add__(self, other):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

        def __sub__(self, other):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

        def __mul__(self, scalar):
            return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

        def __neg__(self):
            return Vector3(-self.x, -self.y, -self.z)

        def __repr__(self):
            return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

        def length(self):
            return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

        def normalized(self):
            ln = self.length()
            if ln == 0:
                return Vector3(0, 0, 0)
            return Vector3(self.x / ln, self.y / ln, self.z / ln)

        def dot(self, other):
            return self.x * other.x + self.y * other.y + self.z * other.z

        def cross(self, other):
            return Vector3(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x,
            )

        def to_array(self):
            return np.array([self.x, self.y, self.z], dtype=np.float32)

        def to_list(self):
            return [self.x, self.y, self.z]

        @staticmethod
        def zero():
            return Vector3(0, 0, 0)

        @staticmethod
        def one():
            return Vector3(1, 1, 1)

        @staticmethod
        def up():
            return Vector3(0, 1, 0)

        @staticmethod
        def right():
            return Vector3(1, 0, 0)

        @staticmethod
        def forward():
            return Vector3(0, 0, -1)

        @staticmethod
        def lerp(a, b, t):
            return a + (b - a) * t

    class Matrix4:
        def __init__(self, data=None):
            if data is not None:
                self.data = np.array(data, dtype=np.float32)
            else:
                self.data = np.identity(4, dtype=np.float32)

        @staticmethod
        def identity():
            return Matrix4()

        @staticmethod
        def translation(v):
            m = Matrix4.identity()
            m.data[0, 3] = v.x
            m.data[1, 3] = v.y
            m.data[2, 3] = v.z
            return m

        @staticmethod
        def rotation_x(angle):
            c = math.cos(angle)
            s = math.sin(angle)
            m = Matrix4.identity()
            m.data[1, 1] = c
            m.data[1, 2] = -s
            m.data[2, 1] = s
            m.data[2, 2] = c
            return m

        @staticmethod
        def rotation_y(angle):
            c = math.cos(angle)
            s = math.sin(angle)
            m = Matrix4.identity()
            m.data[0, 0] = c
            m.data[0, 2] = s
            m.data[2, 0] = -s
            m.data[2, 2] = c
            return m

        @staticmethod
        def rotation_z(angle):
            c = math.cos(angle)
            s = math.sin(angle)
            m = Matrix4.identity()
            m.data[0, 0] = c
            m.data[0, 1] = -s
            m.data[1, 0] = s
            m.data[1, 1] = c
            return m

        @staticmethod
        def scale(v):
            m = Matrix4.identity()
            m.data[0, 0] = v.x
            m.data[1, 1] = v.y
            m.data[2, 2] = v.z
            return m

        @staticmethod
        def perspective(fov, aspect, near, far):
            f = 1.0 / math.tan(fov / 2.0)
            m = Matrix4()
            m.data[0, 0] = f / aspect
            m.data[1, 1] = f
            m.data[2, 2] = (far + near) / (near - far)
            m.data[2, 3] = (2.0 * far * near) / (near - far)
            m.data[3, 2] = -1.0
            m.data[3, 3] = 0.0
            return m

        @staticmethod
        def look_at(eye, target, up):
            f = (target - eye).normalized()
            s = f.cross(up).normalized()
            u = s.cross(f)

            m = Matrix4()
            m.data[0, 0] = s.x
            m.data[0, 1] = s.y
            m.data[0, 2] = s.z
            m.data[1, 0] = u.x
            m.data[1, 1] = u.y
            m.data[1, 2] = u.z
            m.data[2, 0] = -f.x
            m.data[2, 1] = -f.y
            m.data[2, 2] = -f.z
            m.data[0, 3] = -s.dot(eye)
            m.data[1, 3] = -u.dot(eye)
            m.data[2, 3] = f.dot(eye)
            return m

        def __mul__(self, other):
            if isinstance(other, Matrix4):
                return Matrix4(np.dot(self.data, other.data))
            return NotImplemented

        def inverse(self):
            return Matrix4(np.linalg.inv(self.data))

        def transpose(self):
            return Matrix4(self.data.T)
