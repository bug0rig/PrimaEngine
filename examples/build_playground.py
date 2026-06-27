#!/usr/bin/env python3
"""Builds a simpler playground scene to test transforms and rendering."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prima.engine.math_utils import Vector3
from prima.engine.scene import Scene
from prima.engine.objects import Part, Wedge, Sphere, Cylinder, Light
from PyQt5.QtGui import QColor


def build():
    scene = Scene("Playground")
    scene.ambient_color = (0.35, 0.35, 0.45)
    scene.ambient_intensity = 0.4

    ground = Part("Ground")
    ground.size = Vector3(30, 0.5, 30)
    ground.position = Vector3(0, -0.25, 0)
    ground.anchored = True
    ground.material.color = QColor(70, 90, 70)
    scene.add_object(ground)

    parts = [
        (Part("Red Cube"),        (-5, 1.5, 0),  (2, 3, 2),    QColor(200, 50, 50)),
        (Part("Blue Box"),        (5, 1, 0),     (3, 2, 3),    QColor(50, 100, 200)),
        (Sphere("Green Ball"),    (0, 1.5, -5),  (2, 2, 2),    QColor(50, 200, 50)),
        (Wedge("Yellow Ramp"),    (-5, 0.5, 5),  (3, 1.5, 3),  QColor(220, 200, 50)),
        (Cylinder("Gray Pillar"), (5, 2, 5),     (0.8, 4, 0.8), QColor(150, 150, 160)),
        (Part("Purple Platform"), (0, 2, 5),     (4, 0.3, 4),  QColor(160, 80, 200)),
        (Sphere("Orange Ball"),   (-3, 2.5, -3), (1, 1, 1),    QColor(230, 140, 40)),
        (Cylinder("Red Post"),    (3, 1.5, -4),  (0.4, 3, 0.4), QColor(200, 60, 60)),
    ]

    for obj, pos, size, color in parts:
        obj.position = Vector3(*pos)
        obj.size = Vector3(*size)
        obj.anchored = True
        obj.material.color = color
        scene.add_object(obj)

    sun = Light("Sun")
    sun.position = Vector3(15, 25, 10)
    sun.intensity = 1.5
    scene.add_object(sun)

    return scene


def scene_to_dict(scene):
    def obj_to_dict(obj):
        d = {
            "type": obj.object_type, "name": obj.name,
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
        if hasattr(obj, 'color'):
            d["color"] = list(obj.color)
        if obj.object_type == "Light":
            d["light_type"] = obj.light_type
            d["intensity"] = obj.intensity
            d["color"] = list(obj.color)
        return d
    return {
        "name": scene.name,
        "ambient_color": list(scene.ambient_color),
        "ambient_intensity": scene.ambient_intensity,
        "root": obj_to_dict(scene.root),
    }


if __name__ == "__main__":
    scene = build()
    data = scene_to_dict(scene)
    out = os.path.join(os.path.dirname(__file__), "playground.prima")
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved playground to {out}")
    print(f"Total objects: {len(scene.get_all_objects())}")
