"""Command-line interface for running a Prima game server."""

import argparse
import sys
import time
from .server import GameServer


import json


def load_scene_file(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(prog="prima-server", description="Prima Game Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=GameServer.DEFAULT_PORT, help=f"Port (default: {GameServer.DEFAULT_PORT})")
    parser.add_argument("--tick-rate", type=float, default=30.0, help="Physics tick rate (default: 30)")
    parser.add_argument("--scene", type=str, default=None, help="Path to .prima scene file to host")
    parser.add_argument("--session", type=str, default="default", help="Session name for hosted scene")
    args = parser.parse_args()

    server = GameServer(host=args.host, port=args.port)
    server.start()

    if args.scene:
        scene_data = load_scene_file(args.scene)
        from .session import GameSession
        session = GameSession(args.session, scene_data=scene_data, tick_rate=args.tick_rate)
        server.sessions[args.session] = session
        print(f"[Server] Loaded scene '{args.scene}' into session '{args.session}'")

    print(f"[Server] Prima server v0.1.0 running on {args.host}:{args.port}")
    print("[Server] Press Ctrl+C to stop")

    tick_interval = 1.0 / args.tick_rate

    try:
        while True:
            time.sleep(tick_interval)
            server.broadcast_state()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
