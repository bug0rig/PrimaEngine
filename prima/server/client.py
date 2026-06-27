"""Client-side connection to a Prima game server."""

import socket
import threading
from collections import deque
from .protocol import ProtocolMessage, FrameReader


class GameClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reader = FrameReader()
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._inbox: deque[ProtocolMessage] = deque()
        self.player_id: int | None = None
        self.session_name: str | None = None

    def connect(self, host: str, port: int, session: str = "default", player_name: str = ""):
        self.sock.connect((host, port))
        self.sock.setblocking(True)
        self._running = True
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()
        self.send(ProtocolMessage.make_join(session, player_name))

    def disconnect(self):
        self._running = False
        self.send(ProtocolMessage.make_leave())
        try:
            self.sock.close()
        except OSError:
            pass
        if self._thread:
            self._thread.join(timeout=2.0)

    def send(self, msg: ProtocolMessage):
        try:
            self.sock.sendall(msg.encode())
        except (BrokenPipeError, OSError):
            pass

    def send_input(self, actions: dict):
        self.send(ProtocolMessage.make_input(actions))

    def send_chat(self, text: str):
        if self.player_id is not None:
            self.send(ProtocolMessage.make_chat(self.player_id, text))

    def request_session_list(self):
        self.send(ProtocolMessage.make_session_list())

    def poll(self) -> list[ProtocolMessage]:
        with self._lock:
            messages = list(self._inbox)
            self._inbox.clear()
            return messages

    def wait_for(self, msg_type: str, timeout: float = 5.0) -> ProtocolMessage | None:
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            for msg in self.poll():
                if msg.type == msg_type:
                    return msg
            time.sleep(0.01)
        return None

    def _recv_loop(self):
        while self._running:
            try:
                data = self.sock.recv(65536)
            except (BrokenPipeError, OSError):
                break
            if not data:
                break
            messages = self.reader.feed(data)
            with self._lock:
                for msg in messages:
                    if msg.type == "joined":
                        self.player_id = msg.data.get("player_id")
                        self.session_name = msg.data.get("session")
                    self._inbox.append(msg)
        self._running = False
