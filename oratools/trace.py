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

import argparse
import logging
import pprint

from .cli_utils import cli_init, get_next_replay
from .decoder import Decoder
from .demuxer import FileDemuxer


def trace(filename, orders_filter, forced_version):
    logging.info(f'Replay: {filename}')
    with open(filename, 'rb') as f:
        fmt = FileDemuxer(f, forced_version)
        dec = Decoder(fmt.game_info)
        logging.info(f'Game info: {pprint.pformat(fmt.game_info)}')
        for pkt in fmt.read_packet():
            logging.info(f'PKT {pkt}')
            for order in dec.decode_packet(pkt):
                if orders_filter is None or order.type == orders_filter:
                    logging.info(f'  ORD {order}')


def run():
    cli_init()
    parser = argparse.ArgumentParser()
    parser.add_argument('--filter', help='Orders filter')
    parser.add_argument('--forced-version', help='Force a version, useful to trace an invalid/truncated replay')
    parser.add_argument('replay', nargs='+')
    args = parser.parse_args()
    for replay in get_next_replay(args.replay):
        trace(replay, args.filter)
