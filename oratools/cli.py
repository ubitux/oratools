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

import os
import os.path as op
import argparse
import logging

from .buildorder import buildorder
from .chat import chat
from .trace import trace


def _get_next_replay(replays):
    for filename in sorted(replays):
        if op.isdir(filename):
            for root, dirs, files in os.walk(filename):
                for name in files:
                    yield op.join(root, name)
        else:
            yield filename


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--forced-version', help='Force a version, useful to trace an invalid/truncated replay')
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers()

    chat_p = subparsers.add_parser('chat')
    chat_p.add_argument('replay', nargs='+')
    chat_p.set_defaults(func=chat)

    trace_p = subparsers.add_parser('trace')
    trace_p.add_argument('--filter', help='Orders filter')
    trace_p.add_argument('replay', nargs='+')
    trace_p.set_defaults(func=trace)

    buildorder_p = subparsers.add_parser('buildorder')
    buildorder_p.add_argument('replay', nargs='+')
    buildorder_p.set_defaults(func=buildorder)

    args = parser.parse_args()

    if args.func is None:
        parser.print_help()
        return

    logging.basicConfig(level='INFO', format='%(message)s')
    for replay in _get_next_replay(args.replay):
        logging.info(f'Replay: {replay}')
        try:
            args.func(replay, args)
        except:
            logging.error('unable to read %s', replay)
