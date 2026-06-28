from .math_utils import Vector3
from ._physics import PhysicsWorld, RigidBody, CollisionShape, Vec3 as _Vec3, Quat as _Quat
from .materials import PHYSICS_MATERIALS


class PhysicsEngine:
    def __init__(self):
        self._world = PhysicsWorld()
        self._world.solver_iterations = 8
        self._body_map = {}
        self.enabled = True

    @property
    def gravity(self):
        v = self._world.gravity
        return Vector3(v.x, v.y, v.z)

    @gravity.setter
    def gravity(self, v):
        self._world.gravity = _Vec3(v.x, v.y, v.z)

    def _ensure_body(self, obj):
        if obj.id in self._body_map:
            return self._world.get_body(self._body_map[obj.id])
        return None

    def _apply_physics_material(self, body, obj):
        mat_name = getattr(obj, 'physics_material', 'Default')
        mat = PHYSICS_MATERIALS.get(mat_name, PHYSICS_MATERIALS['Default'])
        body.restitution = mat['restitution']
        body.friction = mat['friction']

    def _create_body(self, obj, scene=None):
        body = RigidBody()
        body.set_mass(getattr(obj, 'mass', 1.0))
        body.set_static(getattr(obj, 'anchored', True))
        self._apply_physics_material(body, obj)

        self._update_shape(body, obj)

        po = getattr(obj, 'physics_offset', Vector3.zero())
        body.position = _Vec3(obj.position.x + po.x, obj.position.y + po.y, obj.position.z + po.z)
        body.rotation = _Quat.from_euler(
            obj.rotation.x, obj.rotation.y, obj.rotation.z
        )

        vel = getattr(obj, 'velocity', Vector3.zero())
        body.linear_velocity = _Vec3(vel.x, vel.y, vel.z)

        body_id = self._world.add_body(body)
        self._body_map[obj.id] = body_id

    def _update_shape(self, body, obj):
        obj_type = obj.object_type
        if obj_type == "Sphere":
            body.shape = CollisionShape.make_sphere(obj.size.x / 2)
        elif obj_type == "Part" and getattr(obj, 'shape', 'Box') == "Box":
            hx, hy, hz = obj.size.x / 2, obj.size.y / 2, obj.size.z / 2
            if getattr(obj, 'anchored', True):
                half_extents = [(hx, 0), (hy, 1), (hz, 2)]
                half_extents.sort(key=lambda e: e[0])
                mins = half_extents[0][0]
                maxs = half_extents[2][0]
                if mins > 0 and mins / maxs < 0.15 and mins < 0.5:
                    axis = half_extents[0][1]
                    normal = [0, 0, 0]
                    offset = 0.0
                    if axis == 0:
                        normal[0] = 1.0
                        offset = obj.position.x + hx
                    elif axis == 1:
                        normal[1] = 1.0
                        offset = obj.position.y + hy
                    else:
                        normal[2] = 1.0
                        offset = obj.position.z + hz
                    body.shape = CollisionShape.make_plane(
                        _Vec3(normal[0], normal[1], normal[2]), offset
                    )
                    return
            body.shape = CollisionShape.make_box(hx, hy, hz)
        elif obj_type == "Player":
            body.shape = CollisionShape.make_box(
                obj.size.x / 2, obj.size.y / 2, obj.size.z / 2
            )
            body.restitution = 0.0
            body.friction = 0.2
        else:
            body.set_static(True)

    def _sync_to_body(self, body, obj):
        po = getattr(obj, 'physics_offset', Vector3.zero())
        body.position = _Vec3(obj.position.x + po.x, obj.position.y + po.y, obj.position.z + po.z)
        body.rotation = _Quat.from_euler(
            obj.rotation.x, obj.rotation.y, obj.rotation.z
        )

        vel = getattr(obj, 'velocity', Vector3.zero())
        body.linear_velocity = _Vec3(vel.x, vel.y, vel.z)

        body.set_mass(getattr(obj, 'mass', 1.0))
        body.set_static(getattr(obj, 'anchored', True))
        self._apply_physics_material(body, obj)
        if obj.object_type == "Player":
            body.restitution = 0.0
            body.friction = 0.2

    def _sync_from_body(self, body, obj):
        po = getattr(obj, 'physics_offset', Vector3.zero())
        obj.position = Vector3(body.position.x - po.x, body.position.y - po.y, body.position.z - po.z)

        euler = body.rotation.to_euler()
        obj.rotation = Vector3(euler.x, euler.y, euler.z)

        if hasattr(obj, 'velocity'):
            obj.velocity = Vector3(
                body.linear_velocity.x,
                body.linear_velocity.y,
                body.linear_velocity.z,
            )

    def _step_player(self, obj, scene, dt):
        gravity_val = getattr(scene, 'gravity', Vector3(0, -9.81, 0)).y
        if not hasattr(obj, 'velocity'):
            obj.velocity = Vector3(0, 0, 0)

        vel = obj.velocity

        vel.y += gravity_val * dt

        half_h = getattr(obj, 'collision_height', obj.size.y) / 2
        pos = obj.position
        obj.position = Vector3(pos.x + vel.x * dt, pos.y + vel.y * dt, pos.z + vel.z * dt)

        origin = Vector3(obj.position.x, obj.position.y + 0.5, obj.position.z)
        hit = self.raycast(origin, Vector3(0, -1, 0), half_h + 1.0)
        if hit.hit:
            floor_y = hit.point.y
            player_bottom = obj.position.y - half_h
            if player_bottom <= floor_y:
                pos = obj.position
                obj.position = Vector3(pos.x, floor_y + half_h, pos.z)
                if vel.y < 0:
                    vel.y = 0

    def step(self, scene, dt):
        if not self.enabled:
            return
        if not getattr(scene, 'physics_enabled', True):
            return

        gravity = getattr(scene, 'gravity', None)
        if gravity is not None:
            self.gravity = gravity

        self._world.solver_iterations = getattr(scene, 'solver_iterations', 8)
        self._world.linear_damping = getattr(scene, 'linear_damping', 0.01)
        self._world.angular_damping = getattr(scene, 'angular_damping', 0.01)

        seen = set()
        for obj in scene.get_all_objects():
            if obj.object_type not in ('Part', 'Sphere'):
                continue

            body = self._ensure_body(obj)
            if body is None:
                self._create_body(obj, scene)
                body = self._ensure_body(obj)

            if body is not None:
                self._sync_to_body(body, obj)
                seen.add(obj.id)

        for obj_id in list(self._body_map.keys()):
            if obj_id not in seen:
                body_id = self._body_map[obj_id]
                self._world.remove_body(body_id)
                del self._body_map[obj_id]

        self._world.step(dt)

        for obj in scene.get_all_objects():
            if obj.id not in self._body_map:
                continue
            body = self._world.get_body(self._body_map[obj.id])
            if body is not None:
                self._sync_from_body(body, obj)

        for obj in scene.get_all_objects():
            if obj.object_type == "Player":
                self._step_player(obj, scene, dt)

    def clear(self):
        self._world.clear()
        self._body_map.clear()

    def destroy(self):
        self.clear()
        self._world = None

    def apply_force(self, obj, force):
        if obj.id in self._body_map:
            self._world.apply_force(
                self._body_map[obj.id],
                _Vec3(force.x, force.y, force.z),
                _Vec3(0, 0, 0),
            )

    def raycast(self, origin, direction, max_distance=1000.0):
        return self._world.raycast(
            _Vec3(origin.x, origin.y, origin.z),
            _Vec3(direction.x, direction.y, direction.z),
            max_distance,
        )
