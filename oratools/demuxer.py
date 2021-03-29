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

from . import binutils, miniyaml
from .packet import Packet


class _Demuxer:

    def read_packet(self):
        while True:
            packet = self._read_packet()
            if packet is None:
                break
            yield packet


class FileDemuxer(_Demuxer):

    START_MARKER = -1
    END_MARKER = -2

    def __init__(self, input_file, forced_version=None):
        self._input_file = input_file

        if forced_version:
            self.game_info = {'Root': {'Version': forced_version}}
            return

        # probe footer
        # TODO: check file size
        input_file.seek(-8, 2)
        length, end_marker = binutils.read_data_fmt(input_file, 'ii')
        if end_marker != self.END_MARKER:
            raise Exception(f'Invalid end marker {end_marker}')
        input_file.seek(-(length + 16), 1)
        start_marker, version = binutils.read_data_fmt(input_file, 'ii')
        if start_marker != self.START_MARKER:
            raise Exception(f'Invalid start marker {start_marker}')
        game_data = input_file.read(length)
        length2, = binutils.parse_fmt(game_data, 'i')
        assert length2 == length - 4
        game_yaml = game_data[4:]
        input_file.seek(0, 0)
        self.game_info = miniyaml.load(game_yaml)

    def _read_packet(self):
        return Packet.from_file(self._input_file)


class SocketDemuxer(_Demuxer):

    def __init__(self, socket):
        self._socket = socket

    def _read_packet(self):
        return Packet.from_socket(self._socket)
