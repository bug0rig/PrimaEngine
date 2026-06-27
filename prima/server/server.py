"""TCP game server for Prima.

Listens on a port, accepts client connections, routes them to game sessions.
Supports multiple sessions/rooms simultaneously.
"""

import json
import select
import socket
import threading
import traceback
from .protocol import ProtocolMessage, FrameReader
from .session import GameSession


class ClientConnection:
    def __init__(self, sock: socket.socket, addr, server):
        self.sock = sock
        self.addr = addr
        self.server = server
        self.reader = FrameReader()
        self.player_id: int | None = None
        self.session_name: str | None = None
        self.buffer = bytearray()
        self.sock.setblocking(False)

    def fileno(self) -> int:
        return self.sock.fileno()

    def send(self, msg: ProtocolMessage):
        data = msg.encode()
        try:
            self.sock.sendall(data)
        except (BrokenPipeError, OSError):
            self.server._disconnect(self)

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


class GameServer:
    DEFAULT_PORT = 5777

    def __init__(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.setblocking(False)

        self.clients: dict[int, ClientConnection] = {}
        self.sessions: dict[str, GameSession] = {}
        self._next_client_id = 0
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(16)
        self._running = True
        self._thread = threading.Thread(target=self._server_loop, daemon=True)
        self._thread.start()
        print(f"[Server] Listening on {self.host}:{self.port}")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
        for c in list(self.clients.values()):
            self._disconnect(c)
        for s in list(self.sessions.values()):
            s.stop()
        self.sessions.clear()
        try:
            self._server_sock.close()
        except OSError:
            pass
        print("[Server] Stopped")

    def _server_loop(self):
        while self._running:
            try:
                readable, _, exceptional = select.select(
                    [self._server_sock] + [c.sock for c in self.clients.values()],
                    [],
                    [],
                    0.1,
                )
            except ValueError:
                break

            for sock in readable:
                if sock is self._server_sock:
                    self._accept_new()
                else:
                    client = self._find_client(sock)
                    if client:
                        self._handle_client(client)

            for sock in exceptional:
                client = self._find_client(sock)
                if client:
                    self._disconnect(client)

    def _accept_new(self):
        try:
            csock, addr = self._server_sock.accept()
        except BlockingIOError:
            return
        cid = self._next_client_id
        self._next_client_id += 1
        client = ClientConnection(csock, addr, self)
        self.clients[cid] = client
        print(f"[Server] Client {cid} connected from {addr}")

    def _find_client(self, sock) -> ClientConnection | None:
        for c in self.clients.values():
            if c.fileno() == sock.fileno():
                return c
        return None

    def _handle_client(self, client: ClientConnection):
        try:
            data = client.sock.recv(65536)
        except (BlockingIOError, InterruptedError):
            return
        except (BrokenPipeError, OSError):
            self._disconnect(client)
            return

        if not data:
            self._disconnect(client)
            return

        messages = client.reader.feed(data)
        for msg in messages:
            self._dispatch(client, msg)

    def _dispatch(self, client: ClientConnection, msg: ProtocolMessage):
        try:
            if msg.type == "join":
                self._handle_join(client, msg)
            elif msg.type == "leave":
                self._handle_leave(client)
            elif msg.type == "input":
                self._handle_input(client, msg)
            elif msg.type == "chat":
                self._handle_chat(client, msg)
            elif msg.type == "session_list":
                self._handle_session_list(client)
            elif msg.type == "upload_scene":
                self._handle_upload_scene(client, msg)
            else:
                client.send(ProtocolMessage.make_error(f"Unknown message type: {msg.type}"))
        except Exception:
            traceback.print_exc()
            client.send(ProtocolMessage.make_error("Internal server error"))

    def _handle_join(self, client: ClientConnection, msg: ProtocolMessage):
        session_name = msg.data.get("session", "default")
        player_name = msg.data.get("player_name", "")

        if session_name not in self.sessions:
            self.sessions[session_name] = GameSession(session_name)

        session = self.sessions[session_name]
        pid = session.add_player(player_name)
        client.player_id = pid
        client.session_name = session_name

        client.send(ProtocolMessage.make_joined(session_name, pid))

        scene_data = session.get_scene_data()
        client.send(ProtocolMessage.make_scene(scene_data))

        print(f"[Server] Client {client.addr} joined session '{session_name}' as player {pid}")

    def _handle_leave(self, client: ClientConnection):
        if client.session_name and client.player_id is not None:
            session = self.sessions.get(client.session_name)
            if session:
                session.remove_player(client.player_id)
        self._disconnect(client)

    def _handle_input(self, client: ClientConnection, msg: ProtocolMessage):
        if client.session_name and client.player_id is not None:
            session = self.sessions.get(client.session_name)
            if session:
                session.handle_input(client.player_id, msg.data.get("actions", {}))

    def _handle_chat(self, client: ClientConnection, msg: ProtocolMessage):
        if client.session_name and client.player_id is not None:
            text = msg.data.get("text", "")
            broadcast = ProtocolMessage.make_chat(client.player_id, text)
            for other in self.clients.values():
                if other.session_name == client.session_name and other is not client:
                    other.send(broadcast)

    def _handle_upload_scene(self, client: ClientConnection, msg: ProtocolMessage):
        session_name = msg.data.get("session", "default")
        scene_data = msg.data.get("data")
        if not scene_data:
            client.send(ProtocolMessage.make_error("No scene data in upload"))
            return
        old = self.sessions.get(session_name)
        if old:
            old.stop()
        new_session = GameSession(session_name, scene_data=scene_data)
        self.sessions[session_name] = new_session
        client.send(ProtocolMessage.make_scene_uploaded(session_name))
        print(f"[Server] Scene uploaded to session '{session_name}'")

    def _handle_session_list(self, client: ClientConnection):
        info = [
            {
                "name": s.name,
                "players": len(s.players),
                "tick_rate": s.tick_rate,
                "tick": s._tick,
            }
            for s in self.sessions.values()
        ]
        client.send(ProtocolMessage.make_session_info(info))

    def _disconnect(self, client: ClientConnection):
        if client.session_name and client.player_id is not None:
            session = self.sessions.get(client.session_name)
            if session:
                session.remove_player(client.player_id)
        client.close()
        to_remove = [cid for cid, c in self.clients.items() if c is client]
        for cid in to_remove:
            del self.clients[cid]

    def broadcast_state(self):
        msg_cache = {}
        for client in self.clients.values():
            if not client.session_name:
                continue
            session = self.sessions.get(client.session_name)
            if not session:
                continue
            state = ProtocolMessage.make_state(
                session._tick,
                session.get_state_snapshot(),
            )
            client.send(state)
