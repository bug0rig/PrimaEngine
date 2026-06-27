"""Scene serialization for server-side save/load."""

from prima.engine.scene import Scene, SceneObject
from prima.engine.math_utils import Vector3
from prima.engine.materials import Material
from prima.engine.objects import Part, Camera3D, Light


def scene_to_dict(scene: Scene) -> dict:
    from prima.engine.scene import SceneObject as _SceneObject

    def obj_to_dict(obj):
        d = {
            "type": obj.object_type,
            "name": obj.name,
            "position": [obj.position.x, obj.position.y, obj.position.z],
            "rotation": [obj.rotation.x, obj.rotation.y, obj.rotation.z],
            "size": [obj.size.x, obj.size.y, obj.size.z],
            "visible": obj.visible,
            "children": [obj_to_dict(c) for c in obj.children],
        }
        if hasattr(obj, 'material') and obj.material:
            d["material"] = obj.material.to_dict()
        if hasattr(obj, 'anchored'):
            d["anchored"] = obj.anchored
        if hasattr(obj, 'physics_material'):
            d["physics_material"] = obj.physics_material
        if hasattr(obj, 'mass'):
            d["mass"] = obj.mass
        if hasattr(obj, 'color'):
            d["color"] = list(obj.color)
        if obj.object_type == "Camera":
            d["fov"] = obj.field_of_view
            d["near"] = obj.near_plane
            d["far"] = obj.far_plane
        if obj.object_type == "Light":
            d["light_type"] = obj.light_type
            d["intensity"] = obj.intensity
            d["range"] = obj.range
        if obj.object_type == "Script":
            d["source"] = obj.source
            d["enabled"] = obj.enabled
        return d

    return {
        "name": scene.name,
        "ambient_color": list(scene.ambient_color),
        "ambient_intensity": scene.ambient_intensity,
        "physics_enabled": getattr(scene, 'physics_enabled', True),
        "solver_iterations": getattr(scene, 'solver_iterations', 8),
        "default_restitution": getattr(scene, 'default_restitution', 0.3),
        "default_friction": getattr(scene, 'default_friction', 0.5),
        "linear_damping": getattr(scene, 'linear_damping', 0.01),
        "angular_damping": getattr(scene, 'angular_damping', 0.01),
        "gravity": [scene.gravity.x, scene.gravity.y, scene.gravity.z],
        "root": obj_to_dict(scene.root),
    }


def scene_from_dict(data: dict) -> Scene:
    scene = Scene(data.get("name", "Scene"))
    scene.ambient_color = tuple(data.get("ambient_color", [0.3, 0.3, 0.4]))
    scene.ambient_intensity = data.get("ambient_intensity", 0.3)
    scene.physics_enabled = data.get("physics_enabled", True)
    scene.solver_iterations = data.get("solver_iterations", 8)
    scene.default_restitution = data.get("default_restitution", 0.3)
    scene.default_friction = data.get("default_friction", 0.5)
    scene.linear_damping = data.get("linear_damping", 0.01)
    scene.angular_damping = data.get("angular_damping", 0.01)
    gv = data.get("gravity", [0, -9.81, 0])
    scene.gravity = Vector3(*gv)

    type_map = {
        "Part": Part,
        "Camera": Camera3D,
        "Light": Light,
        "Wedge": __import__("prima.engine.objects", fromlist=["Wedge"]).Wedge,
        "Sphere": __import__("prima.engine.objects", fromlist=["Sphere"]).Sphere,
        "Cylinder": __import__("prima.engine.objects", fromlist=["Cylinder"]).Cylinder,
        "Script": __import__("prima.engine.objects", fromlist=["Script"]).Script,
        "Object": SceneObject,
    }

    def dict_to_obj(d, parent):
        cls = type_map.get(d["type"], SceneObject)
        obj = cls(d.get("name", "Object"))
        obj.object_type = d.get("type", "Object")

        pos = d.get("position", [0, 0, 0])
        obj.position = Vector3(*pos)
        rot = d.get("rotation", [0, 0, 0])
        obj.rotation = Vector3(*rot)
        sz = d.get("size", [1, 1, 1])
        obj.size = Vector3(*sz)
        obj.visible = d.get("visible", True)

        if "material" in d:
            obj.material = Material.from_dict(d["material"])
        if "anchored" in d:
            obj.anchored = d["anchored"]
        if "physics_material" in d:
            obj.physics_material = d["physics_material"]
        if "mass" in d:
            obj.mass = d["mass"]
        if obj.object_type == "Camera":
            obj.field_of_view = d.get("fov", 70)
            obj.near_plane = d.get("near", 0.01)
            obj.far_plane = d.get("far", 1000)
        if obj.object_type == "Light":
            obj.light_type = d.get("light_type", "Directional")
            obj.intensity = d.get("intensity", 1.0)
            obj.range = d.get("range", 50.0)
        if obj.object_type == "Script":
            obj.source = d.get("source", "")
            obj.enabled = d.get("enabled", True)
        if "color" in d:
            c = d["color"]
            obj.color = tuple(c)

        scene.add_object(obj, parent)
        for child_d in d.get("children", []):
            dict_to_obj(child_d, obj)
        return obj

    root_d = data.get("root", {})
    for child_d in root_d.get("children", []):
        dict_to_obj(child_d, scene.root)

    return scene
