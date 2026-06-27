#!/usr/bin/env python3
"""Builds an example city scene and saves it as a .prima file."""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prima.engine.math_utils import Vector3
from prima.engine.scene import Scene
from prima.engine.objects import Part, Wedge, Sphere, Cylinder, Light, Script, Camera3D
from prima.engine.materials import Material
from PyQt5.QtGui import QColor


def build_city_scene():
    scene = Scene("Prima City")
    scene.ambient_color = (0.2, 0.25, 0.35)
    scene.ambient_intensity = 0.35

    # ── Ground ──────────────────────────────────────────────
    ground = Part("Ground")
    ground.size = Vector3(80, 0.5, 80)
    ground.position = Vector3(0, -0.25, 0)
    ground.anchored = True
    ground.material.color = QColor(60, 80, 60)
    scene.add_object(ground)

    # ── Roads (dark gray strips) ────────────────────────────
    road_mat = Material("Road")
    road_mat.color = QColor(50, 50, 55)

    for z in range(-30, 35, 20):
        road = Part(f"Road_Z{z}")
        road.size = Vector3(40, 0.1, 8)
        road.position = Vector3(0, 0, z)
        road.anchored = True
        road.material = road_mat
        scene.add_object(road)

    for x in range(-30, 35, 20):
        road = Part(f"Road_X{x}")
        road.size = Vector3(8, 0.1, 40)
        road.position = Vector3(x, 0, 0)
        road.anchored = True
        road.material = road_mat
        scene.add_object(road)

    # ── Buildings ───────────────────────────────────────────
    buildings_data = [
        # (x, z, w, h, d, color_rgb)
        (-10, -10, 4, 6, 4, (180, 80, 80)),
        (-10,  10, 5, 8, 5, (80, 130, 180)),
        ( 10, -10, 6, 4, 6, (180, 160, 80)),
        ( 10,  10, 4, 10, 4, (120, 80, 160)),
        ( 15, -15, 3, 5, 3, (100, 180, 100)),
        (-15,  15, 5, 7, 5, (200, 120, 60)),
        (  0, -20, 8, 3, 6, (70, 70, 80)),
        (-20,   0, 4, 12, 4, (140, 100, 100)),
        ( 20,   0, 6, 6, 6, (90, 150, 150)),
        (  0,  20, 5, 5, 5, (170, 90, 120)),
    ]

    for i, (x, z, w, h, d, rgb) in enumerate(buildings_data):
        bldg = Part(f"Building_{i+1}")
        bldg.size = Vector3(w, h, d)
        bldg.position = Vector3(x, h / 2, z)
        bldg.anchored = True
        bldg.material.color = QColor(*rgb)
        scene.add_object(bldg)

        roof_h = max(1.0, h * 0.3)
        roof = Wedge(f"Roof_{i+1}")
        roof.size = Vector3(w * 1.1, roof_h, d * 1.1)
        roof.position = Vector3(x, h + roof_h * 0.4, z)
        roof.anchored = True
        roof.material.color = QColor(
            min(255, rgb[0] + 40),
            min(255, rgb[1] + 40),
            min(255, rgb[2] + 40),
        )
        scene.add_object(roof)

    # ── Trees (cylinder trunk + sphere canopy) ──────────────
    tree_positions = [
        (-5, -5), (5, 5), (-15, -20), (20, -5),
        (-25, 10), (25, 15), (-20, -25), (30, -20),
        (-30, 25), (15, -25),
    ]

    for i, (x, z) in enumerate(tree_positions):
        trunk = Cylinder(f"Trunk_{i+1}")
        trunk.size = Vector3(0.3, 1.5, 0.3)
        trunk.position = Vector3(x, 0.75, z)
        trunk.anchored = True
        trunk.material.color = QColor(100, 70, 40)
        scene.add_object(trunk)

        canopy = Sphere(f"Canopy_{i+1}")
        canopy.size = Vector3(1.8, 1.8, 1.8)
        canopy.position = Vector3(x, 2.5, z)
        canopy.anchored = True
        canopy.material.color = QColor(40, 140, 40)
        scene.add_object(canopy)

    # ── Lamp posts ──────────────────────────────────────────
    lamp_positions = [(-10, 0), (10, 0), (0, -10), (0, 10)]

    for i, (x, z) in enumerate(lamp_positions):
        pole = Cylinder(f"LampPole_{i+1}")
        pole.size = Vector3(0.2, 3.0, 0.2)
        pole.position = Vector3(x, 1.5, z)
        pole.anchored = True
        pole.material.color = QColor(60, 60, 60)
        scene.add_object(pole)

        lamp = Sphere(f"LampGlow_{i+1}")
        lamp.size = Vector3(0.5, 0.3, 0.5)
        lamp.position = Vector3(x, 3.2, z)
        lamp.anchored = True
        lamp.material.color = QColor(255, 255, 200)
        scene.add_object(lamp)

    # ── Fence around city ───────────────────────────────────
    for i in range(-30, 35, 5):
        for cx, cz, along_x in [
            (i, -30, True), (i, 30, True),
            (-30, i, False), (30, i, False),
        ]:
            post = Part(f"FencePost_{cx}_{cz}")
            if along_x:
                post.size = Vector3(0.2, 1.0, 0.2)
            else:
                post.size = Vector3(0.2, 1.0, 0.2)
            post.position = Vector3(cx, 0.5, cz)
            post.anchored = True
            post.material.color = QColor(180, 160, 120)
            scene.add_object(post)

    # ── Lighting ────────────────────────────────────────────
    sun = Light("Sun")
    sun.position = Vector3(30, 50, 20)
    sun.light_type = "Directional"
    sun.intensity = 1.8
    sun.color = (1.0, 0.95, 0.9)
    scene.add_object(sun)

    fill = Light("Fill Light")
    fill.position = Vector3(-30, 20, -30)
    fill.light_type = "Directional"
    fill.intensity = 0.4
    fill.color = (0.6, 0.7, 1.0)
    scene.add_object(fill)

    # ── Camera ──────────────────────────────────────────────
    cam = Camera3D("Main Camera")
    cam.position = Vector3(25, 15, 25)
    cam.field_of_view = 70
    scene.add_object(cam)

    # ── Script on a moving platform ─────────────────────────
    platform = Part("Moving Platform")
    platform.size = Vector3(3, 0.3, 3)
    platform.position = Vector3(-25, 0.5, -25)
    platform.anchored = False
    platform.material.color = QColor(200, 100, 50)
    scene.add_object(platform)

    script = Script("Platform Script")
    script.source = """\
# Moving platform script
import math

platform = scene.find_by_name("Moving Platform")
if platform:
    t = engine.elapsed_time * 0.5
    platform.position = Vector3(
        -25 + math.sin(t) * 3,
        0.5 + abs(math.sin(t * 1.5)) * 2,
        -25 + math.cos(t) * 3,
    )
    print(f"Platform at: {platform.position}")
"""
    scene.add_object(script, platform)

    return scene


def scene_to_dict(scene):
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
            d["color"] = list(obj.color)
        if obj.object_type == "Script":
            d["source"] = obj.source
            d["enabled"] = obj.enabled
        return d

    return {
        "name": scene.name,
        "ambient_color": list(scene.ambient_color),
        "ambient_intensity": scene.ambient_intensity,
        "root": obj_to_dict(scene.root),
    }


if __name__ == "__main__":
    scene = build_city_scene()
    data = scene_to_dict(scene)

    out_path = os.path.join(os.path.dirname(__file__), "prima_city.prima")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    obj_count = len(scene.get_all_objects())
    print(f"Built city with {obj_count} objects")
    print(f"Saved to: {out_path}")
    print("Load it in Prima Engine: Ctrl+O -> prima_city.prima")
