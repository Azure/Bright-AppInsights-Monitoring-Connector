# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import (
    Union,
    Optional
)

from pythoncm.entity.entity import Entity

from pythoncm.entity.node import Node
from pythoncm.entity.monitoringmeasurablemetric import MonitoringMeasurableMetric

from pythoncm.entity.metadata.powerstatus import PowerStatus
from pythoncm.entity.devstatus import DevStatus


__all__ = [
    'BrightEntity',
    'BrightNode',
    'BrightMeasurable',
    'BrightPowerStatus',
    'BrightDeviceStatus',
    'BrightEntityMonitoringItem'
]


class BrightEntity(object):
    def __init__(self, entity):
        self.__set_raw_entity(entity)

    def __get_raw_entity(self) -> Entity:
        return self.__raw_entity

    def __set_raw_entity(self, raw_entity: Entity) -> None:
        self.__raw_entity = raw_entity

    def get_raw_entity(self) -> Entity:
        return self.__get_raw_entity()

    @property
    def unique_key(self) -> Optional[int]:
        return getattr(self.__raw_entity, 'uniqueKey', None)


class BrightNode(BrightEntity):
    def __init__(self, node: Node):
        BrightEntity.__init__(self, node)

    @property
    def hostname(self) -> str:
        raw_entity = self.get_raw_entity()

        if getattr(raw_entity, 'hostname', None) is None:
            return 'NA'
        else:
            return getattr(raw_entity, 'hostname', 'NA')

    @property
    def rack_id(self) -> str:
        raw_entity = self.get_raw_entity()

        if getattr(raw_entity, 'rack', None) is None:
            return 'NA'
        else:
            return getattr(raw_entity, 'rack', 'NA')

    @property
    def interfaces(self) -> Optional[dict]:
        raw_entity = self.get_raw_entity()

        interfaces = getattr(raw_entity, 'interfaces', list())
        if interfaces is not None:
            return {
                interface.name: interface
                for interface in getattr(raw_entity, 'interfaces', list())
            }
        else:
            return dict()

    def ip_address(self, interface) -> Optional[str]:
        try:
            return self.interfaces[interface].ip
        except KeyError or AttributeError:
            return None


class BrightMeasurable(BrightEntity):
    def __init__(self, measurable: MonitoringMeasurableMetric):
        BrightEntity.__init__(self, measurable)

    @property
    def name(self) -> Optional[str]:
        raw_entity = self.get_raw_entity()
        return getattr(raw_entity, 'name', None)

    @property
    def parameter(self) -> Optional[str]:
        raw_entity = self.get_raw_entity()
        return getattr(raw_entity, 'parameter', None)

    @property
    def resolve_name(self) -> Optional[str]:
        raw_entity = self.get_raw_entity()
        return getattr(raw_entity, 'resolve_name', None)

    @property
    def type(self) -> Optional[str]:
        raw_entity = self.get_raw_entity()
        return getattr(raw_entity, 'typeClass', None)


class BrightPowerStatus(BrightEntity):
    def __init__(self, power_status: PowerStatus):
        BrightEntity.__init__(self, power_status)

    @property
    def device(self) -> Optional[int]:
        raw_entity = self.get_raw_entity()
        return getattr(raw_entity, 'device', None)

    @property
    def state(self) -> str:
        raw_entity = self.get_raw_entity()
        value = getattr(raw_entity, 'state', 'NA')

        if isinstance(value, str):
            return value
        else:
            return 'NA'

    @property
    def power_state(self) -> Union[int, float]:
        raw_entity = self.get_raw_entity()
        value = getattr(raw_entity, 'state', None)

        if isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, str):
            value = value.upper()

            if value in {'PASS', 'TRUE', 'ON', 'UP'}:
                return 1
            elif value in {'FAIL', 'FALSE', 'OFF', 'DOWN'}:
                return 0
            else:
                return 0
        elif isinstance(value, int) or isinstance(value, float):
            return value
        else:
            return 0


class BrightDeviceStatus(BrightEntity):
    def __init__(self, device_status: DevStatus):
        BrightEntity.__init__(self, device_status)

    @property
    def device(self) -> Optional[int]:
        raw_entity = self.get_raw_entity()
        return getattr(raw_entity, 'refDeviceUniqueKey', None)

    @property
    def status(self) -> str:
        raw_entity = self.get_raw_entity()
        value = getattr(raw_entity, 'status', None)

        if isinstance(value, str):
            return value
        else:
            return 'NA'

    @property
    def ping_status(self) -> Union[int, float]:
        raw_entity = self.get_raw_entity()
        value = getattr(raw_entity, 'status', None)

        if isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, str):
            value = value.upper()

            if value in {'PASS', 'TRUE', 'ON', 'UP'}:
                return 1
            elif value in {'FAIL', 'FALSE', 'OFF', 'DOWN'}:
                return 0
            else:
                return 0
        elif isinstance(value, int) or isinstance(value, float):
            return value
        else:
            return 0


class BrightEntityMonitoringItem(object):
    def __init__(self, monitoring_item: dict):
        self.__set_monitoring_item(monitoring_item)

    def __set_monitoring_item(self, monitoring_item: dict) -> None:
        self.__monitoring_item = monitoring_item

    @property
    def entity(self) -> Optional[str]:
        return self.__monitoring_item.get('entity', None)

    @property
    def measurable(self) -> Optional[str]:
        return self.__monitoring_item.get('measurable', None)

    @property
    def value(self) -> Optional[Union[int, float]]:
        value = self.__monitoring_item.get('value', None)

        if isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, str):
            value = value.upper()

            if value in {'PASS', 'TRUE', 'ON', 'UP'}:
                return 1
            elif value in {'FAIL', 'FALSE', 'OFF', 'DOWN'}:
                return 0
            else:
                return None
        elif isinstance(value, int) or isinstance(value, float):
            return value
        else:
            return None

    @property
    def t0(self) -> int:
        return self.__monitoring_item.get('t0', 0)

    @property
    def t1(self) -> int:
        return self.__monitoring_item.get('t1', 0)
