#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Lobby Forwarder (lobby01.dq-x.net).

    DQX-Stub Server Project
    Copyright (C) 2017  Sepalani

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


class LobbyForwarderRequestHandler(SocketServer.StreamRequestHandler):
    """Send lobby server location properties.

    Example (DQX v3.5.9 Wii):
    00 53 0f 73 2b 00 00 00 00 00 00 00 00 00 00 00  .S.s+...........
    00 32 30 32 2e 36 37 2e 35 39 2e 31 35 34 00 00  .202.67.59.154..
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 02 d9 00 00                                   .....

    Description:
    00 53               - Payload size?
    0f                  - Command type?
    73 2b               - Command ID?
    00 (x8)             - ??? (not present before ~v3.5)
    00 (x4)             - ???
    ASCII string (x64)  - Lobby address
    02 d9               - Lobby port (little endian)
    00 00               - ???
    """
    def handle(self):
        print("[lobby01.dq-x.net] {}:{} connected".format(
            *self.client_address
        ))
        self.wfile.write(self.server.lobby_location)
        print("[lobby01.dq-x.net] {!r} send by {}:{}".format(
            self.rfile.read(255), *self.client_address
        ))


class LobbyForwarderServer(SocketServer.TCPServer):
    def __init__(self, lobby_address, lobby_port, is_legacy, *args, **kwargs):
        SocketServer.TCPServer.__init__(self, *args, **kwargs)
        self.set_lobby_location(lobby_address, lobby_port, is_legacy)

    def pack_address(self, lobby_address, padding=64):
        return bytearray(lobby_address[:padding], "ascii") + \
            bytearray(max(0, padding - len(lobby_address)))

    def set_lobby_location(self, lobby_address, lobby_port, legacy=False):
        command = struct.pack(">BH", 0x0f, 0x732b)
        address = self.pack_address(lobby_address)
        port = struct.pack("<H", lobby_port)
        unknown = bytearray(4)
        if not legacy:
            unknown = bytearray(8) + unknown
        data = command + unknown + address + port + bytearray(2)
        size = struct.pack(">H", len(data))
        self.lobby_location = size + data


if __name__ == "__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-H", "--hostname", action="store", type=str,
                        default="0.0.0.0", dest="host",
                        help="set forwarder hostname")
    parser.add_argument("-P", "--port", action="store", type=int,
                        default=55552, dest="port",
                        help="set forwarder port")
    parser.add_argument("-a", "--lobby-address", action="store", type=str,
                        default="127.0.0.1", dest="lobby_address",
                        help="set lobby address")
    parser.add_argument("-p", "--lobby-port", action="store", type=int,
                        default=55554, dest="lobby_port",
                        help="set lobby port")
    parser.add_argument("-l", "--legacy", action="store_true",
                        help="is protocol before v3.5")
    args = parser.parse_args()

    server = LobbyForwarderServer(
        args.lobby_address, args.lobby_port, args.legacy,
        (args.host, args.port),
        LobbyForwarderRequestHandler,
    )
    try:
        print("Running on {}:{}".format(args.host, args.port))
        print("Forwards to {}:{}".format(args.lobby_address, args.lobby_port))
        server.serve_forever()
    except KeyboardInterrupt:
        print("Closing...")
        server.server_close()
