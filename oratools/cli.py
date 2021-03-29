#
# Copyright (C) 2021
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
from .mappack import mappack


def _get_next_filename(targets):
    for filename in sorted(targets):
        if op.isdir(filename):
            for root, dirs, files in os.walk(filename):
                for name in files:
                    yield op.join(root, name)
        else:
            yield filename


def _replay_opt(fn, args):
    for replay in _get_next_filename(args.replay):
        logging.info(f'Replay: {replay}')
        try:
            fn(replay, args)
        except:
            logging.error('unable to read %s', replay)


def _mappack(args):
    args.maps = [m for m in _get_next_filename(args.maps) if m.endswith('.oramap')]
    mappack(args)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--forced-version', help='Force a version, useful to trace an invalid/truncated replay')
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers()

    chat_p = subparsers.add_parser('chat')
    chat_p.add_argument('replay', nargs='+')
    chat_p.set_defaults(func=lambda args: _replay_opt(chat, args))

    trace_p = subparsers.add_parser('trace')
    trace_p.add_argument('--filter', help='Orders filter')
    trace_p.add_argument('replay', nargs='+')
    trace_p.set_defaults(func=lambda args: _replay_opt(trace, args))

    buildorder_p = subparsers.add_parser('buildorder')
    buildorder_p.add_argument('replay', nargs='+')
    buildorder_p.set_defaults(func=lambda args: _replay_opt(buildorder, args))

    mappack_p = subparsers.add_parser('mappack')
    mappack_p.add_argument('--category', help='Set custom map category')
    mappack_p.add_argument('--title', help='Title reformat, use "{title}" to re-use existing')
    mappack_p.add_argument('--fname', help='File reformat, use "{fname}" to re-use filename')
    mappack_p.add_argument('--overlay', help='Image overlay')
    mappack_p.add_argument('--ext', nargs='+', help='Extension to add (directory with an _extension.yaml file)')
    mappack_p.add_argument('--rm', nargs='+', help='Files to remove (also try to drop associated refs)')
    mappack_p.add_argument('--out-dir', default='.', help='Output directory')
    mappack_p.add_argument('maps', nargs='+')
    mappack_p.set_defaults(func=_mappack)

    args = parser.parse_args()

    if args.func is None:
        parser.print_help()
        return

    logging.basicConfig(level='INFO', format='%(message)s')
    args.func(args)
