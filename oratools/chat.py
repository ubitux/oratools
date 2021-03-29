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

from .cli_utils import cli_init, get_next_replay
from .decoder import Decoder
from .demuxer import FileDemuxer


def chat(filename):
    logging.info(f'Replay: {filename}')
    with open(filename, 'rb') as f:
        fmt = FileDemuxer(f)
        dec = Decoder(fmt.game_info)
        dialogues = []
        for pkt in fmt.read_packet():
            for order in dec.decode_packet(pkt):
                if order.type == 'Handshake' and order.key == b'Chat':  # older version
                    dialog = order.value.decode()
                    team_chat = False  # probably inaccurate
                elif order.type == 'Fields' and order.field == b'Chat':
                    dialog = order.info['target'].decode()
                    team_chat = order.info.get('extra_data') is not None
                else:
                    continue
                name = dec.get_name(pkt.client)
                dialogues.append((name, team_chat, dialog))

        name_padding = max(len(name) for name, _, _ in dialogues)
        for name, team_chat, dialog in dialogues:
            prefix = f'[team]' if team_chat else '[all] '
            name = f'<{name}>'
            logging.info(f'{prefix.ljust(4+2)} {name.rjust(name_padding+2)}  {dialog}')


def run():
    cli_init()
    parser = argparse.ArgumentParser()
    parser.add_argument('replay', nargs='+')
    args = parser.parse_args()
    for replay in get_next_replay(args.replay):
        chat(replay)
