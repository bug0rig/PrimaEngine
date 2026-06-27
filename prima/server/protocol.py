"""Message protocol for Prima server-client communication.

Format: length-prefixed JSON over TCP.
Each message is: [4-byte big-endian length][UTF-8 JSON payload]

Message types:
  - join:          client -> server, { "type": "join", "session": "room_name", "player_name": "..." }
  - joined:        server -> client, { "type": "joined", "session": "...", "player_id": 0 }
  - leave:         client -> server, { "type": "leave" }
  - input:         client -> server, { "type": "input", "actions": {...} }
  - state:         server -> client, { "type": "state", "tick": 0, "objects": [...] }
  - scene:         server -> client, { "type": "scene", "data": {...} }
  - chat:          client <-> server, { "type": "chat", "player_id": 0, "text": "..." }
  - error:         server -> client, { "type": "error", "message": "..." }
  - session_list:  client -> server, { "type": "session_list" }
  - session_info:  server -> client, { "type": "session_info", "sessions": [...] }
  - upload_scene:  client -> server, { "type": "upload_scene", "session": "...", "data": {...} }
  - scene_uploaded: server -> client, { "type": "scene_uploaded", "session": "..." }
"""

import json
import struct
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


class MessageType(str, Enum):
    JOIN = "join"
    JOINED = "joined"
    LEAVE = "leave"
    INPUT = "input"
    STATE = "state"
    SCENE = "scene"
    CHAT = "chat"
    ERROR = "error"
    SESSION_LIST = "session_list"
    SESSION_INFO = "session_info"
    UPLOAD_SCENE = "upload_scene"
    SCENE_UPLOADED = "scene_uploaded"


@dataclass
class ProtocolMessage:
    type: str
    data: dict[str, Any] = field(default_factory=dict)

    def encode(self) -> bytes:
        payload = {"type": self.type, **self.data}
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        header = struct.pack("!I", len(raw))
        return header + raw

    @staticmethod
    def decode(data: bytes) -> "ProtocolMessage":
        payload = json.loads(data.decode("utf-8"))
        msg_type = payload.pop("type", "")
        return ProtocolMessage(type=msg_type, data=payload)

    @staticmethod
    def make_join(session: str, player_name: str = "") -> "ProtocolMessage":
        return ProtocolMessage(MessageType.JOIN, {"session": session, "player_name": player_name})

    @staticmethod
    def make_joined(session: str, player_id: int) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.JOINED, {"session": session, "player_id": player_id})

    @staticmethod
    def make_leave() -> "ProtocolMessage":
        return ProtocolMessage(MessageType.LEAVE)

    @staticmethod
    def make_input(actions: dict) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.INPUT, {"actions": actions})

    @staticmethod
    def make_state(tick: int, objects: list[dict]) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.STATE, {"tick": tick, "objects": objects})

    @staticmethod
    def make_scene(data: dict) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.SCENE, {"data": data})

    @staticmethod
    def make_chat(player_id: int, text: str) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.CHAT, {"player_id": player_id, "text": text})

    @staticmethod
    def make_error(message: str) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.ERROR, {"message": message})

    @staticmethod
    def make_session_list() -> "ProtocolMessage":
        return ProtocolMessage(MessageType.SESSION_LIST)

    @staticmethod
    def make_session_info(sessions: list[dict]) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.SESSION_INFO, {"sessions": sessions})

    @staticmethod
    def make_upload_scene(session: str, data: dict) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.UPLOAD_SCENE, {"session": session, "data": data})

    @staticmethod
    def make_scene_uploaded(session: str) -> "ProtocolMessage":
        return ProtocolMessage(MessageType.SCENE_UPLOADED, {"session": session})


class FrameReader:
    def __init__(self):
        self._buffer = bytearray()
        self._needed = 4

    def feed(self, data: bytes) -> list[ProtocolMessage]:
        self._buffer.extend(data)
        messages = []
        while len(self._buffer) >= 4:
            if self._needed == 4:
                length = struct.unpack("!I", self._buffer[:4])[0]
                self._needed = length
                self._buffer = self._buffer[4:]
            if len(self._buffer) >= self._needed:
                frame = bytes(self._buffer[:self._needed])
                self._buffer = self._buffer[self._needed:]
                self._needed = 4
                messages.append(ProtocolMessage.decode(frame))
            else:
                break
        return messages
