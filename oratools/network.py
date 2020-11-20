#
# Copyright (C) 2020
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import socket


class SocketReader:

    def __init__(self, socket):
        self._socket = socket

    def read(self, n):
        buf = b''
        while True:
            data = self._socket.recv(n)
            if not data:
                raise Exception(f'Unexpected EOF after reading {len(buf)}/{n+len(buf)}')
            buf += data
            n -= len(data)
            if n == 0:
                break
        return buf


def connect(server, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if timeout:
        s.settimeout(timeout)
    s.connect((server, port))
    return s
