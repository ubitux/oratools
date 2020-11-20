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


def parse_fmt(data, fmt):
    n = struct.calcsize(fmt)
    return struct.unpack('<' + fmt, data[:n])


def read_data_fmt(reader, fmt):
    n = struct.calcsize(fmt)
    data = reader.read(n)
    assert len(data) == n
    return parse_fmt(data, fmt)
