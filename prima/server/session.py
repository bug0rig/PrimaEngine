"""Game session — runs a headless Engine and manages connected players."""

import time
import threading
from prima.engine.core import Engine
from prima.engine.math_utils import Vector3


class GameSession:
    """A single game room running a headless Engine instance.

    Each session has a name, runs its own physics simulation at a fixed tick rate,
    and broadcasts object state snapshots to all connected players.
    """

    def __init__(self, name: str, scene_data: dict | None = None, tick_rate: float = 30.0):
        self.name = name
        self.tick_rate = tick_rate
        self.tick_interval = 1.0 / tick_rate

        self.engine = Engine()
        self.engine.running = True

        if scene_data:
            self._load_scene(scene_data)
        else:
            from prima.engine.objects import Part
            floor = Part("Floor")
            floor.size = Vector3(10, 0.5, 10)
            floor.position = Vector3(0, -0.25, 0)
            floor.anchored = True
            self.engine.scene.add_object(floor)

            ball = Part("Ball")
            ball.size = Vector3(0.5, 0.5, 0.5)
            ball.position = Vector3(0, 3, 0)
            ball.anchored = False
            ball.mass = 1.0
            ball.shape = "Sphere"
            self.engine.scene.add_object(ball)

        self.players: dict[int, dict] = {}
        self._next_player_id = 0
        self._tick = 0
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._thread.start()

    def _load_scene(self, scene_data: dict):
        from .serialize import scene_from_dict
        scene = scene_from_dict(scene_data)
        self.engine.set_scene(scene)

    def add_player(self, player_name: str = "") -> int:
        with self._lock:
            pid = self._next_player_id
            self._next_player_id += 1
            self.players[pid] = {
                "id": pid,
                "name": player_name or f"Player {pid}",
                "connected": True,
            }
            return pid

    def remove_player(self, player_id: int):
        with self._lock:
            self.players.pop(player_id, None)

    def handle_input(self, player_id: int, actions: dict):
        pass

    def get_state_snapshot(self) -> list[dict]:
        objects = []
        for obj in self.engine.scene.get_all_objects():
            if obj.object_type in ("Root",):
                continue
            objects.append({
                "id": obj.id,
                "type": obj.object_type,
                "name": obj.name,
                "position": [obj.position.x, obj.position.y, obj.position.z],
                "rotation": [obj.rotation.x, obj.rotation.y, obj.rotation.z],
                "size": [obj.size.x, obj.size.y, obj.size.z],
            })
        return objects

    def get_info(self) -> dict:
        with self._lock:
            return {
                "name": self.name,
                "players": len(self.players),
                "player_list": [p["name"] for p in self.players.values()],
                "tick_rate": self.tick_rate,
                "tick": self._tick,
            }

    def _tick_loop(self):
        last = time.time()
        while self._running:
            now = time.time()
            dt = now - last
            last = now
            self.engine.update()
            self._tick += 1
            elapsed = time.time() - now
            sleep_time = self.tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self.engine.shutdown()

    def get_scene_data(self) -> dict:
        from .serialize import scene_to_dict
        return scene_to_dict(self.engine.scene)
