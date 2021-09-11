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

from PIL import Image
import logging
import os
import os.path as op
import re
import shutil
import sys
import tempfile
import unicodedata
import zipfile


_tag_regex = re.compile(r'\s*\[[^\]]*\]')
_special_regex = re.compile(r'[^A-Za-z0-9]+')
_extension_fname = '_extension.yaml'
_expected_files = {'map.bin', 'map.png', 'map.yaml'}
_colors = dict(zip(
    ('red', 'green', 'yellow', 'blue', 'magenta', 'cyan'),
    (f'\033[0;{c}m' for c in range(31, 37)))
)


def _colored(text, color):
    if not sys.stderr.isatty():
        return text
    return _colors[color] + text + '\033[0m'


class _Extensions:

    def __init__(self, map_yml, ext_dirs, rm_files):
        self._data = dict(
            Rules=set(),
            Sequences=set(),
            Weapons=set(),
            Notifications=set(),
        )
        self._files = set()

        # Prefixes for settings handled by this class system
        self._prefixes = {k + ':' for k in self._data.keys()}

        # Load current map existing map settings
        with open(map_yml) as mapf:
            for line in mapf:
                if ':' not in line:
                    continue
                key, val = line.split(':', maxsplit=1)
                if key not in self._data.keys():
                    continue
                self._add_values(key, val)

        # For every file removal requested, also drop the references in the
        # existing map settings
        for key, val in self._data.items():
            val -= set(rm_files)

        for ext_dir in ext_dirs:
            self._add_extension(ext_dir)

    def handled_line(self, line):
        '''Whether the line setting (coming from map.yaml) is handled by this class'''
        return any(line.startswith(prefix) for prefix in self._prefixes)

    def get_lines(self):
        '''map.yaml lines adjusted to include all the extensions'''
        return [key + ': ' + ', '.join(val) for key, val in self._data.items()]

    def get_files(self):
        '''Extension files (full path) to package into the new map'''
        return self._files

    def _add_extension(self, dirname):
        '''Update internal files and settings with the extension located in dirname'''
        if not op.isdir(dirname):
            raise Exception(f'{dirname} is not a directory')
        ext_files = os.listdir(dirname)

        if _extension_fname not in ext_files:
            raise Exception(f'{_extension_fname} not found in {dirname}')
        ext_files.remove(_extension_fname)

        logging.info(f'[+] Adding extension %s', op.basename(dirname))
        self._files |= set(op.join(dirname, f) for f in ext_files)

        # Parse the extension file and merge its settings with the others
        with open(op.join(dirname, _extension_fname)) as extf:
            for line in extf:
                line = line.rstrip()
                if not line:
                    continue
                key, val = line.split(':', maxsplit=1)
                self._add_values(key, val)

    def _add_values(self, key, val_str):
        values = set(filter(None, (v.strip() for v in val_str.split(','))))
        if key not in self._data.keys():
            raise Exception(f'Unsupported key {key}')
        self._data[key] |= values


def _get_new_map_yml_content(map_yml, extensions, args):
    lines = []

    with open(map_yml) as mapf:
        for line in mapf:
            line = line.rstrip()

            if line.startswith('Title:'):
                cur_title = line.split(':', maxsplit=1)[1].strip()
                new_title = _reformat_title(args, cur_title)
                if new_title != cur_title:
                    logging.info(f'[-] Title: "%s" → "%s"', cur_title, new_title)
                    lines.append(f'Title: {new_title}')
                    continue

            if args.category and line.startswith('Categories:'):
                cur_category = line.split(':', maxsplit=1)[1].strip()
                logging.info(f'[-] Category: "%s" → "%s"', cur_category, args.category)
                lines.append(f'Categories: {args.category}')
                continue

            if extensions.handled_line(line):
                continue

            if not line and not lines[-1]:
                continue

            lines.append(line)

    if lines[-1]:
        lines.append('')
    lines += extensions.get_lines()
    return '\n'.join(lines)


def _extract_title(mapf):
    for line in mapf:
        if line.startswith(b'Title:'):
            return line.split(b':', maxsplit=1)[1].strip().decode()


def _reformat_title(args, title):
    if args.strip_tags:
        title = _tag_regex.sub('', title)
    if args.title:
        title = args.title.format(title=title)
    return title


def mappack(args):

    if args.title and '{title}' not in args.title:
        raise ValueError('Title must contain "{title}"')

    with tempfile.TemporaryDirectory(prefix='oratools-') as tmpdirname:
        for mapfile in args.maps:

            # Extract current map data in a temporary directory
            with zipfile.ZipFile(mapfile) as zipf:

                # Compute a new base filename for the map from its Title
                with zipf.open('map.yaml') as mapf:
                    mapname = _reformat_title(args, _extract_title(mapf))
                    mapname = unicodedata.normalize('NFKD', mapname).encode('ascii', 'ignore').decode()
                    mapname = _special_regex.sub('-', mapname).strip('-')
                    mapname = mapname.lower()

                logging.info('=== Map: %s ===', mapname)
                mapdir = op.join(tmpdirname, mapname)
                map_files = set(op.join(mapdir, f) for f in zipf.namelist())
                zipf.extractall(path=mapdir)

            # Patch map.yaml
            map_yml = op.join(mapdir, 'map.yaml')
            extensions = _Extensions(map_yml, args.ext, args.rm)
            map_yml_content = _get_new_map_yml_content(map_yml, extensions, args)
            with open(map_yml, 'w') as mapf:
                mapf.write(map_yml_content)
            patched_files = {map_yml}

            # Patch map preview overlay
            if args.overlay:
                map_preview = op.join(mapdir, 'map.png')
                bg = Image.open(map_preview)
                fg = Image.open(args.overlay)
                fg = fg.resize(bg.size, Image.LANCZOS)
                bg.paste(fg, mask=fg)
                bg.save(map_preview)
                patched_files |= {map_preview}

            # Identify the list of files not to include in the map
            if args.rm:
                target_removed_files = set(args.rm)
                remove_files = {f for f in map_files if op.basename(f) in target_removed_files}

            # Transfer extension files into the temporary map directory
            src_ext_files = list(extensions.get_files())
            dst_ext_files = [op.join(mapdir, op.basename(f)) for f in src_ext_files]
            for (src, dst) in zip(src_ext_files, dst_ext_files):
                shutil.copyfile(src, dst)
            ext_files = set(dst_ext_files)

            # Zip referenced content into the new map
            os.makedirs(args.out_dir, exist_ok=True)
            out_map = op.join(args.out_dir, mapname + '.oramap')
            logging.info('[+] Creating %s', out_map)
            with zipfile.ZipFile(out_map, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as mapf:
                files = map_files | ext_files | remove_files
                for new_file in sorted(files):
                    if new_file in patched_files:
                        action = _colored('Patch', 'magenta')
                    elif new_file in ext_files:
                        if new_file in map_files:
                            action = _colored('Replace', 'yellow')
                        else:
                            action = _colored('Add', 'green')
                    elif new_file in remove_files:
                        action = _colored('Remove', 'red')
                    else:
                        action = _colored('Copy', 'cyan')

                    logging.info("    [%s] %s", action, op.basename(new_file))
                    if new_file not in remove_files:
                        mapf.write(new_file, arcname=op.basename(new_file))
