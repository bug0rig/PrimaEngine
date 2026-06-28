from .math_utils import Vector3, Matrix4
from .materials import Material


class Connector:
    def __init__(self, name="", position=None, direction=None, conn_type="peg"):
        self.name = name
        self.position = position or Vector3.zero()
        self.direction = direction or Vector3(0, 1, 0)
        self.conn_type = conn_type


class _IDGen:
    _next = 0

    @classmethod
    def get(cls):
        cls._next += 1
        return cls._next


class SceneObject:
    def __init__(self, name="Object"):
        self.id = _IDGen.get()
        self.name = name
        self.parent = None
        self.children = []
        self._position = Vector3.zero()
        self._rotation = Vector3.zero()
        self._size = Vector3.one()
        self._local_matrix = Matrix4.identity()
        self._world_matrix = Matrix4.identity()
        self._dirty = True
        self.visible = True
        self.material = Material.gray()
        self.color = (0.7, 0.7, 0.7)
        self.object_type = "Object"
        self.connectors = []
        self.physics_offset = Vector3.zero()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, v):
        self._position = v
        self._mark_dirty()

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, v):
        self._rotation = v
        self._mark_dirty()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, v):
        self._size = v
        self._mark_dirty()

    def _mark_dirty(self):
        self._dirty = True
        for child in self.children:
            child._mark_dirty()

    def _compute_local_matrix(self):
        t = Matrix4.translation(self._position)
        rx = Matrix4.rotation_x(self._rotation.x)
        ry = Matrix4.rotation_y(self._rotation.y)
        rz = Matrix4.rotation_z(self._rotation.z)
        s = Matrix4.scale(self._size)
        self._local_matrix = t * ry * rx * rz * s

    def get_local_matrix(self):
        if self._dirty:
            self._compute_local_matrix()
            self._dirty = False
        return self._local_matrix

    def get_world_matrix(self):
        if self._dirty:
            self._compute_local_matrix()
            self._dirty = False
        if self.parent:
            self._world_matrix = self.parent.get_world_matrix() * self._local_matrix
        else:
            self._world_matrix = self._local_matrix
        return self._world_matrix

    def get_world_position(self):
        m = self.get_world_matrix()
        return Vector3(m.data[0, 3], m.data[1, 3], m.data[2, 3])

    def set_parent(self, parent):
        if self.parent:
            self.parent.children.remove(self)
        self.parent = parent
        if parent:
            parent.children.append(self)
        self._mark_dirty()

    def add_child(self, child):
        child.set_parent(self)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            child._mark_dirty()

    def find_by_name(self, name):
        if self.name == name:
            return self
        for child in self.children:
            result = child.find_by_name(name)
            if result:
                return result
        return None

    def find_by_id(self, obj_id):
        if self.id == obj_id:
            return self
        for child in self.children:
            result = child.find_by_id(obj_id)
            if result:
                return result
        return None

    def get_all_objects(self):
        objs = [self]
        for child in self.children:
            objs.extend(child.get_all_objects())
        return objs

    def set_color(self, r, g, b):
        self.color = (r, g, b)
        if hasattr(self, 'material') and self.material:
            self.material.set_color(int(r * 255), int(g * 255), int(b * 255))

    def destroy(self):
        if self.parent:
            self.parent.remove_child(self)
        self.children.clear()

    def duplicate(self):
        obj = SceneObject(f"{self.name} (Copy)")
        obj.position = self.position
        obj.rotation = self.rotation
        obj.size = self.size
        obj.visible = self.visible
        obj.material = self.material
        obj.object_type = self.object_type
        obj.color = self.color
        obj.connectors = [Connector(c.name, c.position, c.direction, c.conn_type) for c in self.connectors]
        obj.physics_offset = self.physics_offset
        for child in self.children:
            obj.add_child(child.duplicate())
        return obj

    def __repr__(self):
        return f"<{self.object_type} '{self.name}'>"


class Scene:
    def __init__(self, name="Scene"):
        self.name = name
        self.root = SceneObject("Root")
        self.root.object_type = "Root"
        self.active_camera = None
        self.ambient_color = (0.3, 0.3, 0.4)
        self.ambient_intensity = 0.5
        self.fog_enabled = False
        self.fog_color = (0.5, 0.5, 0.6)
        self.fog_density = 0.01
        self.gravity = Vector3(0, -9.81, 0)
        self.physics_enabled = True
        self.solver_iterations = 8
        self.default_restitution = 0.3
        self.default_friction = 0.5
        self.linear_damping = 0.01
        self.angular_damping = 0.01

    def add_object(self, obj, parent=None):
        if parent is None:
            parent = self.root
        parent.add_child(obj)
        return obj

    def remove_object(self, obj):
        obj.destroy()

    def find_by_name(self, name):
        return self.root.find_by_name(name)

    def find_by_id(self, obj_id):
        return self.root.find_by_id(obj_id)

    def get_all_objects(self):
        return self.root.get_all_objects()

    def clear(self):
        self._destroy_tree(self.root)
        self.root = SceneObject("Root")
        self.root.object_type = "Root"

    def _destroy_tree(self, obj):
        for child in list(obj.children):
            self._destroy_tree(child)
            child.parent = None
        obj.children.clear()
