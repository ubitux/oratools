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

def _vlq_deserialize(data):
    n = nbytes = 0
    for i, digit in enumerate(data):
        n |= (digit & 0x7f) << (7 * i)
        nbytes += 1
        if not (digit & 0x80):
            break
    return n, nbytes


def _vlq_serialize(n):
    data = []
    while True:
        val = n & 0x7f
        n >>= 7
        data.append(val | 0x80 if n else val)
        if not n:
            break
    return bytes(data)


def parse_string(data):
    length, nbytes = _vlq_deserialize(data)
    string = data[nbytes:nbytes+length]
    return string, nbytes + length


def serialize_string(s):
    data_length = _vlq_serialize(len(s))
    return data_length + s
