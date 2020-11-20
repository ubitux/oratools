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

import pprint

from . import binutils, csharp, miniyaml
from .packet import Packet


class _Order:

    @property
    def type(self):
        return self.__class__.__name__[len('Order'):]

    # XXX: is this exhaustive?
    _TARGET_STRING_DATA = (
        b'HandshakeRequest',
        b'HandshakeResponse',
        b'SaveTraitData',
        b'StartGame',
        b'SyncClientPings',
        b'SyncInfo',
        b'SyncLobbyClients',
        b'SyncLobbyGlobalSettings',
        b'SyncLobbySlots',
    )

    @classmethod
    def _decode_target_string(cls, field, target_string):
        if field in cls._TARGET_STRING_DATA:
            return miniyaml.load(target_string)
        return target_string


class OrderSyncHash(_Order):

    def __init__(self, sync_hash, defeat_state=None):
        self.sync_hash = sync_hash
        self.defeat_state = defeat_state

    @classmethod
    def from_data(cls, data, game_version: str, orders_version: int):
        if orders_version is not None and orders_version >= 11:
            sync_hash, defeat_state = binutils.parse_fmt(data, 'IQ')
            obj = cls(sync_hash, defeat_state)
            obj.data = data[:4+8]
        else:
            sync_hash, = binutils.parse_fmt(data, 'I')
            obj = cls(sync_hash)
            obj.data = data[:4]
        return obj

    def __str__(self):
        s = f'[SyncHash] hash:0x{self.sync_hash:08X}'
        if self.defeat_state is not None:
            s += f' defeat_state:0x{self.defeat_state:016X}'
        return s


class OrderDisconnect(_Order):

    @classmethod
    def from_data(cls, data, game_version: str, orders_version: int):
        assert len(data) == 0
        return cls()

    def __str__(self):
        return '[Disconnect]'


class OrderHandshake(_Order):

    def __init__(self, key, value, orders_version):
        self.key = key
        self.value = value
        self.orders_version = orders_version

    @classmethod
    def from_data(cls, data, game_version: str, orders_version: int):
        key, key_size = csharp.parse_string(data)
        value, value_size = csharp.parse_string(data[key_size:])
        value = cls._decode_target_string(key, value)
        orders_version = None
        if key == b'HandshakeResponse':
            orders_protocol = value['Handshake'].get('OrdersProtocol')
            if orders_protocol is not None:
                orders_version = int(orders_protocol)
        return cls(key, value, orders_version)

    def __str__(self):
        return f'[Handshake] type:{self.key.decode()} value:\n{pprint.pformat(self.value)}'


class OrderFields(_Order):

    _FLAG_TARGET        = 1 << 0
    _FLAG_EXTRAACTORS   = 1 << 1
    _FLAG_TARGETSTRING  = 1 << 2
    _FLAG_QUEUED        = 1 << 3
    _FLAG_EXTRALOCATION = 1 << 4
    _FLAG_EXTRADATA     = 1 << 5
    _FLAG_TARGETISCELL  = 1 << 6
    _FLAG_SUBJECT       = 1 << 7
    _FLAG_GROUPED       = 1 << 8

    _TARGET_TYPE_INVALID, _TARGET_TYPE_ACTOR, _TARGET_TYPE_TERRAIN, _TARGET_TYPE_FROZEN_ACTOR = list(range(4))

    def __init__(self, field, info):
        self.field = field
        self.info = info

    @classmethod
    def from_data(cls, data, game_version: str, orders_version: int):
        field, field_size = csharp.parse_string(data)
        data = data[field_size:]

        info = {}

        if orders_version is None:
            orders_version = 7

        if orders_version < 8:
            info['subject_id'], = binutils.parse_fmt(data, 'I')
            data = data[4:]

        flags_fmt, flags_size = ('B', 1) if orders_version < 11 else ('h', 2)
        flags, = binutils.parse_fmt(data, flags_fmt)
        data = data[flags_size:]

        if flags & cls._FLAG_SUBJECT:  # added in orders_version == 8
            info['subject_id'], = binutils.parse_fmt(data, 'I')
            data = data[4:]

        if flags & cls._FLAG_TARGET:
            target_type = data[0]
            data = data[1:]

            if target_type == cls._TARGET_TYPE_ACTOR:
                info['target_actor_id'], = binutils.parse_fmt(data, 'I')
                data = data[4:]

            elif target_type == cls._TARGET_TYPE_FROZEN_ACTOR:
                info['player_actor_id'], info['frozen_actor_id'] = binutils.parse_fmt(data, 'II')
                data = data[8:]

            elif target_type == cls._TARGET_TYPE_TERRAIN:
                if flags & cls._FLAG_TARGETISCELL:
                    info['cell'], info['sub_cell'] = binutils.parse_fmt(data, 'ib')
                    data = data[5:]
                else:
                    info['pos'] = binutils.parse_fmt(data, 'iii')
                    data = data[12:]

        if flags & cls._FLAG_TARGETSTRING:
            target_string, target_string_size = csharp.parse_string(data)
            info['target'] = cls._decode_target_string(field, target_string)
            data = data[target_string_size:]

        if flags & cls._FLAG_EXTRAACTORS:  # added in orders_version 10
            count, = binutils.parse_fmt(data, 'i')
            data = data[4:]
            info['extra_actors'] = binutils.parse_fmt(data, 'I' * count)
            data = data[4 * count:]

        if flags & cls._FLAG_EXTRALOCATION:
            info['extra_location'], = binutils.parse_fmt(data, 'i')
            data = data[4:]

        if flags & cls._FLAG_EXTRADATA:
            info['extra_data'], = binutils.parse_fmt(data, 'I')
            data = data[4:]

        if flags & cls._FLAG_GROUPED:  # added in orders_version == 11
            count, = binutils.parse_fmt(data, 'i')
            data = data[4:]
            info['grouped_actors'] = binutils.parse_fmt(data, 'I' * count)
            data = data[4 * count:]

        return cls(field, info)

    def __str__(self):
        return f'[Fields] field:{self.field.decode()} info:\n{pprint.pformat(self.info)}'


class Decoder:

    _order_map = {
        0x65: OrderSyncHash,
        0xbf: OrderDisconnect,
        0xfe: OrderHandshake,
        0xff: OrderFields,
    }

    def __init__(self, game_info: dict):
        self._orders_version = None
        self._game_info = game_info
        self._game_version = game_info['Root']['Version']
        self._client_names = {}

        # FIXME: only valid with red alert default game speed
        self._time_step = 40  # ms
        self._order_latency = 3

    @staticmethod
    def _get_client_names(sync_info):
        client_names = {}
        for client, client_data in sync_info.items():
            if not client.startswith('Client@'):
                continue
            client_id = int(client[len('Client@'):])
            client_name = client_data['Name']
            client_names[client_id] = client_name
        return client_names

    def decode_packet(self, pkt: Packet):
        data = pkt.data
        while data:
            order_type = data[0]
            order_cls = self._order_map[order_type]
            order = order_cls.from_data(data[1:], self._game_version, self._orders_version)

            if order.type == 'Handshake':
                if self._orders_version is None:
                    self._orders_version = order.orders_version
                if order.key == b'SyncInfo':  # old method
                    self._client_names = self._get_client_names(order.value)
            elif order.type == 'Fields':
                if order.field == b'SyncInfo':
                    self._client_names = self._get_client_names(order.info['target'])

            data = data[len(data):]
            yield order

    def get_name(self, client_id):
        return self._client_names[client_id]

    def get_frame_time(self, frame_id):
        tick = frame_id * self._order_latency
        total_ms = tick * self._time_step
        total_s = total_ms // 1000
        total_m = total_s // 60
        ms = total_ms % 1000
        s = total_s % 60
        m = total_m
        return f'{m:02}:{s:02}.{ms:03}'
