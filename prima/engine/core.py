import time
import gc
from .scene import Scene
from .rendering import Renderer
from .physics import PhysicsEngine
from .math_utils import Vector3


class Engine:
    def __init__(self):
        self.scene = Scene()
        self.renderer = None
        self.physics = PhysicsEngine()
        self.running = False
        self.paused = False
        self.time_scale = 1.0
        self._last_time = 0.0
        self._delta_time = 0.0
        self._elapsed_time = 0.0
        self.frame_count = 0
        self.fps = 0.0
        self._frame_timer = 0.0

    def initialize(self):
        self.renderer = Renderer()
        self._last_time = time.time()
        return True

    def shutdown(self):
        if self.renderer:
            self.renderer.destroy()
            self.renderer = None
        if self.physics:
            self.physics.destroy()
            self.physics = None
        if self.scene:
            self.scene.clear()
            self.scene = None
        gc.collect()
        self.running = False

    def update(self):
        current = time.time()
        self._delta_time = (current - self._last_time) * self.time_scale
        self._last_time = current
        if self.running and not self.paused:
            self._elapsed_time += self._delta_time
            self.physics.step(self.scene, min(self._delta_time, 0.05))
        self.frame_count += 1
        self._frame_timer += self._delta_time
        if self._frame_timer >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self._frame_timer = 0.0

    def render(self, view_matrix, proj_matrix, camera_pos):
        if self.renderer:
            self.renderer.render(self.scene, view_matrix, proj_matrix, camera_pos)

    def set_scene(self, scene):
        if scene is not self.scene:
            self.physics.clear()
        self.scene = scene

    @property
    def delta_time(self):
        return self._delta_time

    @property
    def elapsed_time(self):
        return self._elapsed_time
