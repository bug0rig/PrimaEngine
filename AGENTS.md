# Prima Engine — Project Rules

## Build & Run
- Build C++ module: `pip install -e . --no-build-isolation` in project root
- Run editor: `python main.py` from project root
- The C++ module installs to `~/.local/lib/python3/site-packages/prima/engine/_physics.cpython-312.so`
- After editing `src/physics.cpp` or `src/math_utils.cpp`, rebuild with `pip install -e . --no-build-isolation`

## Code Conventions
- Python: snake_case for methods/vars, PascalCase for classes
- C++: PascalCase for structs/methods, snake_case for members/vars
- OpenGL 3.3+ Compatibility Profile
- PyQt5 + PyOpenGL for GUI; numpy for mesh data
- C++ hot paths via nanobind (Vector3, Matrix4, physics engine)

## Physics Engine (src/physics.cpp)
- Contact normal convention: n points FROM body_b TOWARD body_a
  - Impulse: body_a += impulse, body_b -= impulse
  - Position correction: body_a += corr, body_b -= corr
- GJK contact: normal from body_a→body_b center direction (not from simplex)
- Support points in gjk_contact are projected onto contact normal to strip perpendicular components (prevent bogus lever arms)
- Impulse NOT divided by solver_iterations — vn>0 guard prevents over-application
- `add_body()` returns world-assigned body ID (Python `body.id` ≠ world ID)
- `get_body()` uses `nb::rv_policy::reference` to avoid double-free
- `set_mass()` / `set_static()` update inv_mass internally — DO NOT assign fields directly
- `CollisionShape.make_*()` are static factory methods returning new objects — must assign result

## Physics Wrapper (prima/engine/physics.py)
- `PhysicsEngine._body_map[obj.id] = body_id` for object↔body tracking
- `step()` syncs Python obj → C++ body before stepping, then C++ body → Python obj after
- New objects get `_create_body()`, existing ones get `_sync_to_body()`
- Deleted objects have bodies removed from world

## Scene Config
- `Scene.gravity` = Vector3 (default: 0, -9.81, 0)
- `Scene.physics_enabled` = bool (default: True)
- `Scene.solver_iterations` = int (default: 8)
- `Scene.linear_damping` = float (default: 0.01)
- `Scene.angular_damping` = float (default: 0.01)
- `Scene.default_restitution` = float (default: 0.3)
- `Scene.default_friction` = float (default: 0.5)

## Physics Materials (prima/engine/materials.py)
- 10 presets: Concrete, Wood, Metal, Rubber, Plastic, Stone, Glass, Ice, Carpet, Default
- Each has: `restitution`, `friction`, `density`
- `PHYSICS_MATERIAL_NAMES` = sorted keys
- Material change in editor auto-computes mass = density × volume
- `_apply_physics_material(body, obj)` applies restitution+friction from preset

## Editor Pattern
- `MainWindow` creates Engine, splits: Hierarchy | Viewport+Console/Tutorials | Properties
- `PropertyPanel.show_object(obj)` rebuilds property UI for selected object
- `Viewport3D._tick()` runs freecam → `update()` → `paintGL()`
- `paintGL()` calls `engine.update()` then `engine.render()` then grid + selection overlay
- `engine.running = False` in editor, `True` in Runtime — gates physics stepping
- `EditorToolbar._play_scene()` deep-copies scene and creates RuntimeWindow
- `EditorToolbar._save_scene()` / `_load_scene()` use JSON .prima format

## Scene Serialization (prima/server/serialize.py)
- `scene_to_dict(scene)` / `scene_from_dict(data)` — shared by editor and server
- Both `EditorToolbar` and `GameSession` use these functions
- .prima JSON format: root {name, ambient*, physics*, gravity, root {children tree}}

## Server Module (prima/server/)
- `GameServer(host, port)` — TCP server; `start()` / `stop()`; broadcasts state at tick rate
- `GameSession(name, scene_data, tick_rate)` — headless Engine + player management; runs tick loop in daemon thread
- `GameClient()` — `connect()` / `disconnect()` / `poll()` / `wait_for(type, timeout)`
- `ProtocolMessage` — JSON-over-TCP with 4-byte length prefix; `FrameReader` for buffered parsing
- `MessageType`: join, joined, leave, input, state, scene, chat, error, session_list, session_info, upload_scene, scene_uploaded
- Run server: `python -m prima.server.cli` or `prima-server` (if installed), optionally `--scene file.prima --session name`
- Server sends scene snapshot on join, then delta/state updates at configurable tick rate (default 30Hz)
- `broadcast_state()` sends current object positions/rotations/sizes to all clients in each session
- Upload scene: client sends `upload_scene` with scene dict, server replaces session's running scene

## Game Client (prima/client/)
- `GameWindow()` — QMainWindow with connect dialog, GameViewport, input relay, state sync
- Run client: `python -m prima.client.game_client` or `prima-client` (if installed)
- Connect flow: dialog -> join -> receive scene -> render -> poll state at tick rate
- `GameViewport._apply_state()` syncs server object transforms to local scene tree by id
- Input relay: WASD + mouse captured on right-click, sent as `input` messages to server

## Editor Upload
- `EditorToolbar._upload_to_server()` — "Upload to Server..." button in toolbar
- Connects to server as temporary client, sends scene dict via `upload_scene` message
- Server replaces existing session or creates a new one with uploaded scene

## Testing
- Run test: `python -c "from prima.engine._physics import *"` (verifies module loads)
- Physics scenarios: Run `prima_physics_test.py` from scripts/ if present
- Manual: create objects in editor, click Play, observe physics behavior
- Server test: `python -c "from prima.server import GameServer; s=GameServer(port=15777); s.start(); s.stop()"`
