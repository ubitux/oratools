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

import struct

from . import binutils, network


class Packet:

    # received packets are [length:i32][client:i32][frame:i32][orders:length-4]
    # sent     packets are [length:i32]            [frame:i32][orders:length-4]
    # replay   packets are [client:i32][length:i32][frame:i32][orders:length-4]

    def __init__(self, client: int, frame: int, data: bytes):
        self.client = client
        self.frame = frame
        self.data = data

    @classmethod
    def from_socket(cls, s):
        reader = network.SocketReader(s)
        return cls.from_file(reader, swapped=False)

    @classmethod
    def from_file(cls, f, swapped=True):
        length, client, frame = binutils.read_data_fmt(f, 'iii')

        # For some reason, client and length are swapped in replays
        if swapped:
            client, length = length, client

        if length < 4:
            return None
        data = f.read(length - 4)
        assert len(data) == length - 4
        return cls(client, frame, data)

    def send(self, s):
        s.send(struct.pack('ii', len(self.data) + 4, self.frame) + self.data)

    def __str__(self):
        return f'client:{self.client} frame:{self.frame} datalen:{len(self.data)}'
