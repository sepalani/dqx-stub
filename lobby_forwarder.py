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

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


class LobbyForwarderRequestHandler(SocketServer.StreamRequestHandler):
    """Send lobby server location properties.

    Example:
    00 53 0f 73 2b 00 00 00 00 00 00 00 00 00 00 00  .S.s+...........
    00 32 30 32 2e 36 37 2e 35 39 2e 31 35 34 00 00  .202.67.59.154..
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 02 d9 00 00                                   .....

    Description:
    00 53               - Payload size?
    0f 73 2b 00         - ???
    00 (x11)            - Padding?
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
    def __init__(self, lobby_address, lobby_port, *args, **kwargs):
        SocketServer.TCPServer.__init__(self, *args, **kwargs)
        self.set_lobby_location(lobby_address, lobby_port)

    def set_lobby_location(self, lobby_address, lobby_port):
        unknown = bytearray([0x0f, 0x73, 0x2b, 0x00])
        ip = bytearray(lobby_address[:64], "ascii")
        ip += bytearray(max(0, 64 - len(ip)))
        port = bytearray([lobby_port & 0xFF, (lobby_port >> 8) & 0xFF])
        data = unknown + bytearray(11) + ip + port + bytearray(2)
        size = bytearray([(len(data) >> 8) & 0xFF, len(data) & 0xFF])
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
    args = parser.parse_args()

    server = LobbyForwarderServer(
        args.lobby_address, args.lobby_port,
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
