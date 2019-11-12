# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
import six
import time

from typing import Iterable

import pythoncm

from pythoncm.cluster import Cluster
from pythoncm.settings import Settings

from pythoncm.entity.node import Node
from pythoncm.entity.monitoringmeasurablemetric import MonitoringMeasurableMetric

from exceptions import BrightClusterConnectionError

from classes import (
    BrightNode,
    BrightMeasurable,
    BrightPowerStatus,
    BrightDeviceStatus,
    BrightEntityMonitoringItem,
)

__all__ = [
    'BrightCluster'
]


class BrightCluster(object):
    def __init__(self, host_ip: str, cert_filepath: str, key_filepath: str):
        self.__set_host_ip(host_ip)
        self.__set_cert_filepath(cert_filepath)
        self.__set_key_filepath(key_filepath)

        settings = self.__create_settings()
        self.__set_settings(settings)

        cluster = self.__create_cluster()
        self.__set_cluster(cluster)

    def __get_host_ip(self) -> str:
        return self.__host_ip

    def __set_host_ip(self, host_ip: str) -> None:
        self.__host_ip = host_ip

    def __get_cert_filepath(self) -> str:
        return self.__cert_filepath

    def __set_cert_filepath(self, cert_filepath: str) -> None:
        self.__cert_filepath = cert_filepath

    def __get_key_filepath(self) -> str:
        return self.__key_filepath

    def __set_key_filepath(self, key_filepath: str) -> None:
        self.__key_filepath = key_filepath

    def __get_settings(self) -> Settings:
        return self.__settings

    def __set_settings(self, settings: Settings) -> None:
        self.__settings = settings

    def __get_cluster(self) -> Cluster:
        return self.__cluster

    def __set_cluster(self, cluster: Cluster) -> None:
        self.__cluster = cluster

    def __create_settings(self) -> Settings:
        ca_filepath = None

        for path in pythoncm.__path__:
            filepath = os.path.join(path, r'etc/cacert.pem')
            if os.path.isfile(filepath):
                ca_filepath = filepath
                break

        host_ip = self.__get_host_ip()

        cert_filepath = self.__get_cert_filepath()
        key_filepath = self.__get_key_filepath()

        settings = Settings(host=host_ip, port=8081, cert_file=cert_filepath, key_file=key_filepath,
                            ca_file=ca_filepath)

        if not settings.check_ca_certificate_file():
            raise BrightClusterConnectionError('CA file is not defined or not exist')

        if not settings.check_certificate_files():
            raise BrightClusterConnectionError('PEM or KEY files are not defined or not exist')

        return settings

    def __create_cluster(self) -> Cluster:
        settings = self.__get_settings()
        return Cluster(settings, follow_redirect=Cluster.REDIRECT_NONE)

    def __entities_lookup(self, keywords: Iterable[str] = None, instances: Iterable = None) -> list:
        keywords_lookup = set(keywords) if keywords is not None else set()
        instances_lookup = tuple(instances) if instances is not None else tuple([])

        cluster = self.__get_cluster()

        entities = []
        for entity in six.itervalues(cluster.entities):
            if isinstance(entity, instances_lookup) or instances is None:
                if keywords is None:
                    entities.append(entity)
                else:
                    if getattr(entity, 'name', None) is not None:
                        if entity.name in keywords_lookup:
                            entities.append(entity)
                    elif getattr(entity, 'resolve_name', None) is not None:
                        if entity.resolve_name in keywords_lookup:
                            entities.append(entity)

        return entities

    def get_nodes(self, keywords: Iterable[str] = None) -> dict:
        nodes = self.__entities_lookup(keywords=keywords, instances=[Node])

        result = dict()
        for node in nodes:
            bright_node = BrightNode(node)
            result[bright_node.unique_key] = bright_node

        return result

    def get_measurables(self, keywords: Iterable[str] = None) -> dict:
        measurables = self.__entities_lookup(keywords=keywords, instances=[MonitoringMeasurableMetric])

        result = dict()
        for measurable in measurables:
            bright_measurable = BrightMeasurable(measurable)
            result[bright_measurable.unique_key] = bright_measurable

        return result

    def get_latest_monitoring_data(self, entities: dict, measurables: dict) -> dict:
        raw_entity = [entity.get_raw_entity() for entity in entities.values()]
        raw_measurables = [measurable.get_raw_entity() for measurable in measurables.values()]

        cluster = self.__get_cluster()

        try:
            monitoring_data = cluster.monitoring.get_latest_monitoring_data(raw_entity, raw_measurables).raw.get(
                'items', list())
        except AttributeError:
            return dict()

        result = dict()
        for item in monitoring_data:
            bright_monitoring_item = BrightEntityMonitoringItem(item)
            result.setdefault(bright_monitoring_item.entity, []).append(bright_monitoring_item)

        return result

    def get_dump_monitoring_data(self, entities: dict, measurables: dict) -> dict:
        raw_entity = [entity.get_raw_entity() for entity in entities.values()]
        raw_measurables = [measurable.get_raw_entity() for measurable in measurables.values()]

        cluster = self.__get_cluster()

        try:
            monitoring_data = cluster.monitoring.dump_monitoring_data(raw_entity, raw_measurables).raw.get(
                'items', list())
        except AttributeError:
            return dict()

        result = dict()
        for item in monitoring_data:
            bright_monitoring_item = BrightEntityMonitoringItem(item)
            result.setdefault(bright_monitoring_item.entity, []).append(bright_monitoring_item)

        return result

    def get_sample_now(self, entities: dict, measurables: dict) -> dict:
        raw_entity = [entity.get_raw_entity() for entity in entities.values()]
        raw_measurables = [measurable.get_raw_entity() for measurable in measurables.values()]

        cluster = self.__get_cluster()

        try:
            monitoring_data = cluster.monitoring.sample_now(raw_entity, raw_measurables).raw.get('items', list())
        except AttributeError:
            return dict()

        result = dict()
        for item in monitoring_data:
            bright_monitoring_item = BrightEntityMonitoringItem(item)
            result.setdefault(bright_monitoring_item.entity, []).append(bright_monitoring_item)

        return result

    def get_monitoring_data(self, entities: dict, measurables: dict, interval: int) -> dict:
        raw_entity = [entity.get_raw_entity() for entity in entities.values()]
        raw_measurables = [measurable.get_raw_entity() for measurable in measurables.values()]

        cluster = self.__get_cluster()

        try:
            monitoring_data = cluster.monitoring.get_latest_monitoring_data(raw_entity, raw_measurables).raw.get(
                'items', list())
        except AttributeError:
            return dict()

        result = dict()
        for item in monitoring_data:
            bright_monitoring_item = BrightEntityMonitoringItem(item)
            if bright_monitoring_item.t1 >= (int(time.time()) - (interval * 60)) * 1000:
                result.setdefault(bright_monitoring_item.entity, []).append(bright_monitoring_item)

        return result

    def get_power_status(self, devices: dict) -> dict:
        cluster = self.__get_cluster()

        power_status = cluster.parallel.power_status(devices)

        if len(power_status) == 2:
            if power_status[0]:

                result = dict()
                for item in power_status[1]:
                    bright_power_status = BrightPowerStatus(item)
                    result[bright_power_status.device] = bright_power_status

                return result
            else:
                return dict()
        else:
            return dict()

    def get_device_status(self, devices: dict) -> dict:
        cluster = self.__get_cluster()

        device_status = cluster.parallel.device_status(devices)

        result = dict()
        for item in device_status:
            bright_device_status = BrightDeviceStatus(item)
            result[bright_device_status.device] = bright_device_status

        return result
