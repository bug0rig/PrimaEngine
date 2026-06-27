from .math_utils import Matrix4, Vector3
import math


def build_view_matrix(position, rotation):
    pitch = rotation.x
    yaw = rotation.y

    cos_p = math.cos(pitch)
    sin_p = math.sin(pitch)
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)

    forward = Vector3(sin_y * cos_p, sin_p, cos_y * cos_p).normalized()
    target = position + forward
    return Matrix4.look_at(position, target, Vector3.up())


def build_projection_matrix(fov, aspect, near, far):
    return Matrix4.perspective(math.radians(fov), aspect, near, far)
