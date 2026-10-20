#!/usr/bin/env python3
"""Small Samsung websocket remote with Keychain-backed token retention."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import ssl
import struct
import subprocess
import time
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime_config import tv_host  # noqa: E402

TV_HOST = tv_host()
CLIENT_NAME = "Daybreak TV Control"
KEYCHAIN_ACCOUNT = CLIENT_NAME
KEYCHAIN_SERVICE = os.environ.get(
    "DAYBREAK_TV_KEYCHAIN_SERVICE", f"daybreak-samsung-tv-{TV_HOST}"
)


def keychain_token() -> str | None:
    result = subprocess.run(
        [
            "/usr/bin/security",
            "find-generic-password",
            "-a",
            KEYCHAIN_ACCOUNT,
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    token = result.stdout.strip()
    return token if result.returncode == 0 and token else None


def save_keychain_token(token: str) -> None:
    try:
        result = subprocess.run(
            [
                "/usr/bin/security",
                "add-generic-password",
                "-U",
                "-a",
                KEYCHAIN_ACCOUNT,
                "-s",
                KEYCHAIN_SERVICE,
                "-w",
                token,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        raise RuntimeError("Could not retain the Samsung remote token in Keychain") from None
    if result.returncode:
        raise RuntimeError("Could not retain the Samsung remote token in Keychain")


class WebSocket:
    def __init__(self, token: str | None, timeout: float = 90.0) -> None:
        raw_socket = socket.create_connection((TV_HOST, 8002), timeout=timeout)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.socket = context.wrap_socket(raw_socket, server_hostname=TV_HOST)
        self.socket.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        name = base64.b64encode(CLIENT_NAME.encode("utf-8")).decode("ascii")
        path = "/api/v2/channels/samsung.remote.control?name=" + quote(name)
        if token:
            path += "&token=" + quote(token)
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {TV_HOST}:8002\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.socket.sendall(request.encode("ascii"))
        header = self._read_until(b"\r\n\r\n")
        if not header.startswith(b"HTTP/1.1 101"):
            raise RuntimeError("Samsung remote websocket upgrade was rejected")
        accept = base64.b64encode(
            hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
            ).digest()
        )
        if accept not in header:
            raise RuntimeError("Samsung remote websocket returned an invalid accept key")

    def _read_until(self, marker: bytes) -> bytes:
        result = bytearray()
        while marker not in result:
            chunk = self.socket.recv(4096)
            if not chunk:
                raise EOFError("Samsung remote closed during handshake")
            result.extend(chunk)
        return bytes(result)

    def _exact(self, count: int) -> bytes:
        result = bytearray()
        while len(result) < count:
            chunk = self.socket.recv(count - len(result))
            if not chunk:
                raise EOFError("Samsung remote websocket closed")
            result.extend(chunk)
        return bytes(result)

    def receive(self) -> dict[str, object]:
        while True:
            first, second = self._exact(2)
            opcode = first & 0x0F
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._exact(8))[0]
            payload = self._exact(length)
            if opcode == 8:
                raise EOFError("Samsung remote websocket closed")
            if opcode == 9:
                self._send_frame(payload, opcode=10)
                continue
            if opcode == 1:
                return json.loads(payload.decode("utf-8"))

    def _send_frame(self, payload: bytes, opcode: int = 1) -> None:
        mask = os.urandom(4)
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.socket.sendall(bytes(header) + mask + masked)

    def send_json(self, payload: dict[str, object]) -> None:
        self._send_frame(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    def close(self) -> None:
        try:
            self._send_frame(b"", opcode=8)
        finally:
            self.socket.close()


def connect() -> WebSocket:
    websocket = WebSocket(keychain_token())
    event = websocket.receive()
    if event.get("event") != "ms.channel.connect":
        raise RuntimeError(
            "Samsung remote authorization was not accepted: "
            + str(event.get("event", "unknown event"))
        )
    data = event.get("data")
    if isinstance(data, dict):
        token = data.get("token")
        if isinstance(token, str) and token:
            save_keychain_token(token)
    return websocket


def remote_key(websocket: WebSocket, key: str, command: str = "Click") -> None:
    websocket.send_json(
        {
            "method": "ms.remote.control",
            "params": {
                "Cmd": command,
                "DataOfCmd": key,
                "Option": "false",
                "TypeOfRemote": "SendRemoteKey",
            },
        }
    )


def launch_app(
    websocket: WebSocket, app_id: str, action_type: str = "DEEP_LINK"
) -> None:
    websocket.send_json(
        {
            "method": "ms.channel.emit",
            "params": {
                "event": "ed.apps.launch",
                "to": "host",
                "data": {
                    "action_type": action_type,
                    "appId": app_id,
                    "metaTag": "",
                },
            },
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("pair", help="authorize or refresh the retained TV token")
    key_parser = actions.add_parser("key", help="send a Samsung remote key")
    key_parser.add_argument("key_name")
    actions.add_parser("poweroff", help="send a held power-button press")
    launch_parser = actions.add_parser("launch", help="launch an app by ID")
    launch_parser.add_argument("app_id")
    args = parser.parse_args()
    websocket = connect()
    try:
        if args.action == "key":
            remote_key(websocket, args.key_name)
        elif args.action == "launch":
            launch_app(websocket, args.app_id)
        elif args.action == "poweroff":
            remote_key(websocket, "KEY_POWER", "Press")
            time.sleep(5)
            remote_key(websocket, "KEY_POWER", "Release")
        print("Samsung remote control authorized; token retained in Keychain")
    finally:
        websocket.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
