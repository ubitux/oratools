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


def _find_target_in_queue(queue, target):
    for i, item in enumerate(queue):
        qframe, qtarget, qcount = item
        if qtarget == target:
            return i
    #logging.warning(f'anomaly detected: can not find target {target} in {queue}')
    return -1


def _remove_queue_items(queue, target, count):
    i = _find_target_in_queue(queue, target)
    if i == -1:
        return
    qframe, qtarget, qcount = queue[i]
    remain = qcount - count
    if remain <= 0:
        queue.pop(i)
        if remain:
            #logging.info(f'[{target}] {qcount=} {count=} -> {remain=}')
            _remove_queue_items(queue, target, -remain)
    else:
        queue[i] = (qframe, qtarget, qcount - count)


def buildorder(filename):
    logging.info(f'Replay: {filename}')
    with open(filename, 'rb') as f:

        builds = {}
        queues = {}

        fmt = FileDemuxer(f)
        dec = Decoder(fmt.game_info)
        for pkt in fmt.read_packet():
            for order in dec.decode_packet(pkt):
                if order.type != 'Fields':
                    continue
                if order.field == b'StartProduction':
                    queue = queues.get(pkt.client, [])
                    #logging.info(f'{pkt.client} start {order.info} q:{queue}')
                    target = order.info['target']
                    count = order.info['extra_data']
                    queue.append((pkt.frame, target, count))
                    queues[pkt.client] = queue
                elif order.field == b'PlaceBuilding':
                    queue = queues[pkt.client]
                    #logging.info(f'{pkt.client} place {order.info} q:{queue}')
                    target = order.info['target']

                    i = _find_target_in_queue(queue, target)
                    if i == -1:
                        continue
                    start_frame, qtarget, qcount = queue[i]
                    _remove_queue_items(queue, target, 1)

                    b = builds.get(pkt.client, [])
                    b.append((start_frame, pkt.frame, target))
                    builds[pkt.client] = b
                elif order.field == b'CancelProduction':
                    queue = queues[pkt.client]
                    #logging.info(f'{pkt.client} cancel {order.info} q:{queue}')
                    target = order.info['target']
                    count = order.info['extra_data']
                    _remove_queue_items(queue, target, count)

        for client, build in builds.items():
            name = dec.get_name(client)
            logging.info(f'{name}:')
            for start_frame, end_frame, struct in build:
                t0 = dec.get_frame_time(start_frame)
                t1 = dec.get_frame_time(end_frame)
                logging.info(f'  {t0} → {t1}: {struct.decode()}')


def run():
    cli_init()
    parser = argparse.ArgumentParser()
    parser.add_argument('replay', nargs='+')
    args = parser.parse_args()
    for replay in get_next_replay(args.replay):
        buildorder(replay)
