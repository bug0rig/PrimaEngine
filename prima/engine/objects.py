from .scene import SceneObject
from .math_utils import Vector3, Matrix4
from .materials import Material


class Part(SceneObject):
    def __init__(self, name="Part"):
        super().__init__(name)
        self.object_type = "Part"
        self.shape = "Box"
        self.material = Material.gray()
        self.can_collide = True
        self.anchored = False
        self.mass = 1.0
        self.velocity = Vector3.zero()
        self.color = (0.7, 0.7, 0.7)
        self.physics_material = "Default"

    def set_color(self, r, g, b):
        self.color = (r, g, b)
        self.material.set_color(int(r * 255), int(g * 255), int(b * 255))


class Wedge(SceneObject):
    def __init__(self, name="Wedge"):
        super().__init__(name)
        self.object_type = "Wedge"
        self.material = Material.gray()
        self.anchored = False
        self.color = (0.7, 0.7, 0.7)


class Cylinder(SceneObject):
    def __init__(self, name="Cylinder"):
        super().__init__(name)
        self.object_type = "Cylinder"
        self.material = Material.gray()
        self.anchored = False
        self.color = (0.7, 0.7, 0.7)


class Sphere(SceneObject):
    def __init__(self, name="Sphere"):
        super().__init__(name)
        self.object_type = "Sphere"
        self.material = Material.gray()
        self.anchored = False
        self.mass = 1.0
        self.velocity = Vector3.zero()
        self.color = (0.7, 0.7, 0.7)
        self.physics_material = "Default"


class Mesh3D(SceneObject):
    def __init__(self, name="Mesh"):
        super().__init__(name)
        self.object_type = "Mesh"
        self.mesh_path = ""
        self.material = Material.gray()


class Camera3D(SceneObject):
    def __init__(self, name="Camera"):
        super().__init__(name)
        self.object_type = "Camera"
        self.field_of_view = 70.0
        self.near_plane = 0.01
        self.far_plane = 1000.0
        self.viewport_width = 800
        self.viewport_height = 600


class Light(SceneObject):
    def __init__(self, name="Light"):
        super().__init__(name)
        self.object_type = "Light"
        self.light_type = "Directional"
        self.color = (1.0, 1.0, 1.0)
        self.intensity = 1.0
        self.range = 50.0
        self.spot_angle = 45.0
        self.shadows_enabled = True


class Script(SceneObject):
    def __init__(self, name="Script"):
        super().__init__(name)
        self.object_type = "Script"
        self.source = ""
        self.enabled = True
        self.run_on_start = True
