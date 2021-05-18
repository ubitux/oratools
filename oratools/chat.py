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

from .decoder import Decoder
from .demuxer import FileDemuxer


def chat(filename, args):
    with open(filename, 'rb') as f:
        fmt = FileDemuxer(f, args.forced_version)
        dec = Decoder(fmt.game_info)
        dialogues = []
        try:
            for pkt in fmt.read_packet():
                for order in dec.decode_packet(pkt):
                    if order.type == 'Handshake' and order.key == b'Chat':  # older version
                        dialog = order.value.decode()
                        source = 'all'  # probably inaccurate
                    elif order.type == 'Fields' and order.field == b'Chat':
                        dialog = order.info['target'].decode()
                        source = 'all' if order.info.get('extra_data') is None else 'team'
                    elif order.type == 'Fields' and order.field == b'Message':
                        dialog = order.info['target'].decode()
                        source = 'server'
                    else:
                        continue
                    name = dec.get_name(pkt.client) if source != 'server' else None
                    dialogues.append((name, source, dialog))
        except ValueError as e:
            logging.error(e)

        if not dialogues:
            return

        name_padding = max(len(name) for name, _, _ in dialogues if name is not None)
        source_padding = max(len(source) for _, source, _ in dialogues if source is not None)
        for name, source, dialog in dialogues:
            prefix = f'[{source}]'
            name = f'<{name}>' if name is not None else ''
            logging.info(f'{prefix.ljust(source_padding+2)} {name.rjust(name_padding+2)}  {dialog}')
