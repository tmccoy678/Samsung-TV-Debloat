#!/usr/bin/env python3
"""Minimal direct SDB client for the Samsung TU7000 deployment endpoint."""

from __future__ import annotations

import argparse
import os
import socket
import struct
import sys
import time
from pathlib import Path


def command_value(name: str) -> int:
    return struct.unpack("<I", name.encode("ascii"))[0]


def packet(name: str, arg0: int = 0, arg1: int = 0, data: bytes = b"") -> bytes:
    value = command_value(name)
    header = struct.pack(
        "<6I",
        value,
        arg0,
        arg1,
        len(data),
        sum(data) & 0xFFFFFFFF,
        value ^ 0xFFFFFFFF,
    )
    return header + data


class SDB:
    def __init__(self, host: str, port: int = 26101, timeout: float = 10.0):
        self.sock = socket.create_connection((host, port), timeout)
        self.sock.settimeout(timeout)
        self.local_id = 1
        self.remote_id = 0
        self.sock.sendall(packet("CNXN", 0x01000000, 4096, b"host::\0"))
        name, _, _, banner = self.recv_packet()
        if name != "CNXN":
            raise RuntimeError(f"expected CNXN, received {name}")
        self.banner = banner.rstrip(b"\0").decode("utf-8", "replace")

    def close(self) -> None:
        self.sock.close()

    def recv_exact(self, size: int) -> bytes:
        result = bytearray()
        while len(result) < size:
            chunk = self.sock.recv(size - len(result))
            if not chunk:
                raise EOFError("SDB connection closed")
            result.extend(chunk)
        return bytes(result)

    def recv_packet(self) -> tuple[str, int, int, bytes]:
        header = self.recv_exact(24)
        value, arg0, arg1, length, checksum, magic = struct.unpack("<6I", header)
        name = struct.pack("<I", value).decode("ascii", "replace")
        if magic != (value ^ 0xFFFFFFFF):
            raise RuntimeError(f"invalid magic for {name}")
        data = self.recv_exact(length) if length else b""
        if (sum(data) & 0xFFFFFFFF) != checksum:
            raise RuntimeError(f"invalid checksum for {name}")
        return name, arg0, arg1, data

    def open_stream(self, service: str) -> None:
        data = service.encode("utf-8") + b"\0"
        self.sock.sendall(packet("OPEN", self.local_id, 0, data))
        while True:
            name, arg0, arg1, _ = self.recv_packet()
            if name == "OKAY" and arg1 == self.local_id:
                self.remote_id = arg0
                return
            if name == "CLSE":
                raise RuntimeError(f"service closed while opening: {service}")

    def write_stream(self, data: bytes) -> bytes:
        received = bytearray()
        self.sock.sendall(packet("WRTE", self.local_id, self.remote_id, data))
        while True:
            name, arg0, arg1, incoming = self.recv_packet()
            if name == "OKAY" and arg1 == self.local_id:
                return bytes(received)
            if name == "WRTE":
                self.sock.sendall(packet("OKAY", self.local_id, arg0))
                received.extend(incoming)
            elif name == "CLSE":
                raise RuntimeError("stream closed during write")

    def read_payload(self) -> bytes:
        while True:
            name, arg0, _, data = self.recv_packet()
            if name == "WRTE":
                self.sock.sendall(packet("OKAY", self.local_id, arg0))
                return data
            if name == "CLSE":
                raise RuntimeError("stream closed before response")

    def read_stream(self) -> bytes:
        result = bytearray()
        while True:
            name, arg0, _, data = self.recv_packet()
            if name == "WRTE":
                result.extend(data)
                self.sock.sendall(packet("OKAY", self.local_id, arg0))
            elif name == "CLSE":
                self.sock.sendall(packet("CLSE", self.local_id, arg0))
                return bytes(result)


def sync_record(name: str, payload: bytes = b"") -> bytes:
    return name.encode("ascii") + struct.pack("<I", len(payload)) + payload


def push(host: str, source: Path, destination: str) -> None:
    client = SDB(host)
    try:
        print(f"connected: {client.banner}")
        client.open_stream("sync:")
        remote_spec = f"{destination},33261".encode("utf-8")
        client.write_stream(sync_record("SEND", remote_spec))
        # Older Samsung TV SDB daemons reset the transport when a WRTE frame
        # exceeds their small host-side buffer. TizenBrew Installer uses 1420.
        with source.open("rb") as handle:
            while chunk := handle.read(1420):
                client.write_stream(sync_record("DATA", chunk))
        response = client.write_stream(b"DONE" + struct.pack("<I", int(time.time())))
        if not response:
            response = client.read_payload()
        if response[:4] == b"FAIL":
            length = struct.unpack("<I", response[4:8])[0]
            raise RuntimeError(response[8 : 8 + length].decode("utf-8", "replace"))
        if response[:4] != b"OKAY":
            raise RuntimeError(f"unexpected sync response: {response[:200]!r}")
        print(f"pushed {source.stat().st_size} bytes to {destination}")
    finally:
        client.close()


def pull(host: str, source: str, destination: Path) -> None:
    client = SDB(host, timeout=60.0)
    try:
        print(f"connected: {client.banner}")
        client.open_stream("sync:")
        response = bytearray(
            client.write_stream(sync_record("RECV", source.encode("utf-8")))
        )
        response.extend(client.read_stream())
        offset = 0
        output = bytearray()
        while offset + 8 <= len(response):
            name = bytes(response[offset : offset + 4])
            length = struct.unpack("<I", response[offset + 4 : offset + 8])[0]
            offset += 8
            if name == b"DONE":
                destination.write_bytes(output)
                print(f"pulled {len(output)} bytes from {source}")
                return
            if name == b"FAIL":
                message = bytes(response[offset : offset + length]).decode(
                    "utf-8", "replace"
                )
                raise RuntimeError(message)
            if name != b"DATA" or offset + length > len(response):
                raise RuntimeError(f"invalid sync pull response at offset {offset - 8}")
            output.extend(response[offset : offset + length])
            offset += length
        raise RuntimeError("sync pull response ended before DONE")
    finally:
        client.close()


def shell(host: str, command: str) -> None:
    client = SDB(host, timeout=180.0)
    try:
        print(f"connected: {client.banner}")
        client.open_stream(f"shell:0 {command}")
        output = client.read_stream()
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    push_parser = sub.add_parser("push")
    push_parser.add_argument("source", type=Path)
    push_parser.add_argument("destination")
    pull_parser = sub.add_parser("pull")
    pull_parser.add_argument("source")
    pull_parser.add_argument("destination", type=Path)
    shell_parser = sub.add_parser("shell")
    shell_parser.add_argument("command")
    args = parser.parse_args()
    if args.action == "push":
        push(args.host, args.source, args.destination)
    elif args.action == "pull":
        pull(args.host, args.source, args.destination)
    else:
        shell(args.host, args.command)


if __name__ == "__main__":
    main()
