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

import logging
import pprint

from .decoder import Decoder
from .demuxer import FileDemuxer


def trace(filename, args):
    orders_filter = args.filter
    with open(filename, 'rb') as f:
        fmt = FileDemuxer(f, args.forced_version)
        dec = Decoder(fmt.game_info)
        logging.info(f'Game info: {pprint.pformat(fmt.game_info)}')
        try:
            for pkt in fmt.read_packet():
                logging.info(f'PKT {pkt}')
                for order in dec.decode_packet(pkt):
                    if orders_filter is None or order.type == orders_filter:
                        logging.info(f'  ORD {order}')
        except ValueError as e:
            logging.error(e)
