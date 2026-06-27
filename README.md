# Prima Engine

A 3D game engine. Build scenes in the editor, host them on a server, play them from a client.

Still early. Physics works (rigid bodies, collisions, stacking). The editor is functional. Multiplayer is there but basic — you can upload a scene to a server and connect with the game client.

## What's inside

- **Editor** — PyQt5 + OpenGL 3.3. Hierarchy panel, property editor, transform tools. Runs the same physics as the game.
- **Server** — headless TCP server. Hosts game sessions, runs physics at a tick rate, broadcasts state to clients. You can run it on your machine, or set up a dedicated box.
- **Client** — connects to a server, renders the scene, sends input (WASD + mouse look). Minimal — just enough to test multiplayer.
- **Physics** — custom C++ engine (nanobind). GJK for collisions, sequential impulse solver, friction, restitution. Wraps JoltPhysics for the broadphase.
- **Tutorials** — built into the editor. Interactive tours that walk you through the UI.

## Quick start

```bash
# Install dependencies and build C++ module
python install.py install

# Launch the editor
python install.py run
# or
python main.py
```

### Run a server

```bash
python install.py server --port 5777 --scene my_scene.prima
# or directly
python -m prima.server.cli --port 5777 --scene my_scene.prima
```

### Connect a client

```bash
python -m prima.client.game_client
```

Opens a dialog — enter the server IP, port, session name, and your player name.

## Project structure

```
prima/
  engine/       Core: scene graph, physics, rendering, materials, scripting
  editor/       PyQt5 editor: viewport, hierarchy, properties, toolbar, tutorials
  server/       TCP server, game sessions, client connection protocol
  client/       Game client window with connect dialog and input relay
  runtime/      Standalone local player (single-player play mode)
```

## License

MIT. JoltPhysics (included as a submodule) is also MIT.
