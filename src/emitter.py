# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
import time
import json
import logging
import threading

from typing import Iterable
from applicationinsights.logging import LoggingHandler

from cluster import BrightCluster

from exceptions import (
    EmitMetricsTimeoutError,
    RefreshClusterTimeoutError
)

from logger import TraceLogger

from constants import WORKINGDIR


__all__ = [
    'ApplicationInsightsEmitter'
]


class ApplicationInsightsEmitter(object):
    def __init__(self, bright_host_ip: str, metrics: Iterable[str], instrumentation_key: str):
        self.__set_bright_host_ip(bright_host_ip)
        self.__set_metrics(metrics)
        self.__set_instrumentation_key(instrumentation_key)

        bright_cluster = self.__create_bright_cluster()
        self.__set_bright_cluster(bright_cluster)

        emit_handler = LoggingHandler(instrumentation_key)
        emit_handler.setLevel(logging.DEBUG)
        self.__set_emit_handler(emit_handler)

        emitter = logging.getLogger('application-insights')
        emitter.setLevel(logging.DEBUG)
        emitter.addHandler(emit_handler)
        self.__set_emitter(emitter)

        mutex = threading.Lock()
        self.__set_mutex(mutex)

    def __get_bright_host_ip(self) -> str:
        return self.__host_ip

    def __set_bright_host_ip(self, host_ip: str) -> None:
        self.__host_ip = host_ip

    def __get_metrics(self) -> Iterable[str]:
        return self.__metrics

    def __set_metrics(self, metrics: Iterable[str]):
        self.__metrics = metrics

    def __get_instrumentation_key(self):
        return self.__instrumentation_key

    def __set_instrumentation_key(self, instrumentation_key):
        self.__instrumentation_key = instrumentation_key

    def __get_bright_cluster(self) -> BrightCluster:
        return self.__bright_cluster

    def __set_bright_cluster(self, bright_cluster: BrightCluster) -> None:
        self.__bright_cluster = bright_cluster

    def __get_emit_handler(self):
        return self.__emit_handler

    def __set_emit_handler(self, emit_handler):
        self.__emit_handler = emit_handler

    def __get_emitter(self):
        return self.__emitter

    def __set_emitter(self, emitter):
        self.__emitter = emitter

    def __get_mutex(self) -> threading.Lock:
        return self.__mutex

    def __set_mutex(self, mutex: threading.Lock) -> None:
        self.__mutex = mutex

    def __create_bright_cluster(self) -> BrightCluster:
        bright_host_ip = self.__get_bright_host_ip()

        bright_cert_filepath = os.path.join(WORKINGDIR, r'certs/bright-cert.pem')
        bright_key_filepath = os.path.join(WORKINGDIR, r'certs/bright-key.key')

        return BrightCluster(bright_host_ip, bright_cert_filepath, bright_key_filepath)

    def emit_metrics(self, emit_interval: int) -> None:
        TraceLogger.info('Emit Metrics - Started')

        start_time = time.time()

        try:
            metrics = self.__get_metrics()
            bright_cluster = self.__get_bright_cluster()

            mutex = self.__get_mutex()

            # thread-safe logic
            mutex.acquire()
            TraceLogger.info('Emit Metrics - Acquire Lock')

            nodes = bright_cluster.get_nodes()
            measurables = bright_cluster.get_measurables(metrics)

            TraceLogger.info('Emit Metrics - Release Lock')
            mutex.release()
            # end

            # fetch monitoring data in background
            monitoring_data = bright_cluster.get_monitoring_data(nodes, measurables, emit_interval)

            # checking for timeout
            if (time.time() - start_time) / 60 > emit_interval:
                raise EmitMetricsTimeoutError('Emit Metrics unable to complete the job in given time period')

            for unique_key, bright_node in nodes.items():
                node_metric_data = dict()

                node_metric_data['Hostname'] = bright_node.hostname
                node_metric_data['RackId'] = bright_node.rack_id  # rack id will NA for non bare metal clusters

                for monitoring_item in monitoring_data.get(unique_key, list()):
                    # filtering out invalid metrics
                    if monitoring_item.value is None or monitoring_item.measurable is None:
                        continue

                    measurable = measurables.get(monitoring_item.measurable)

                    # filtering out invalid metrics
                    if measurable is None:
                        continue
                    if measurable.name is None or measurable.type is None:
                        continue

                    node_metric_data[measurable.name] = monitoring_item.value

                emitter = self.__get_emitter()

                message = json.dumps(node_metric_data)

                # TODO: remove below line
                print(message)

                emitter.info(message)

                emit_handler = self.__get_emit_handler()
                emit_handler.flush()

        except EmitMetricsTimeoutError:
            TraceLogger.error('Emit Metrics - Terminated: Unable to complete Emit Metrics process in '
                              '{0} minutes'.format(emit_interval))
        except Exception as ex:
            TraceLogger.error('Emit Metrics - Failed: {0}'.format(ex))

        TraceLogger.info('Emit Metrics - Ended')

    def refresh_cluster(self, refresh_interval: int) -> None:
        TraceLogger.info('Refreshing Cluster - Started')

        start_time = time.time()

        try:
            # refreshing cluster in background
            bright_cluster = self.__create_bright_cluster()

            # checking for timeout
            if (time.time() - start_time) / 60 > refresh_interval:
                raise RefreshClusterTimeoutError('Refresh Cluster unable to complete the job in given time period')

            mutex = self.__get_mutex()

            # thread-safe logic
            mutex.acquire()
            TraceLogger.info('Refreshing Cluster - Acquire Lock')

            self.__set_bright_cluster(bright_cluster)

            TraceLogger.info('Refreshing Cluster - Release Lock')
            mutex.release()
            # end

        except RefreshClusterTimeoutError:
            TraceLogger.error('Refresh Cluster - Terminated: Unable to complete Refresh Cluster process in '
                              '{0} minutes'.format(refresh_interval))
        except Exception as ex:
            TraceLogger.error('Refresh Cluster - Failed: {0}'.format(ex))

        TraceLogger.info('Refreshing Cluster - Ended')

    def start(self, emit_interval: int, refresh_interval: int) -> None:
        TraceLogger.info('Monitoring Connector - Started')
        sleep_count = 0

        # TODO: remove below lines
        print(self.__get_instrumentation_key())

        emit_metrics = threading.Thread()
        refresh_cluster = threading.Thread()

        while True:
            TraceLogger.info('Monitoring Connector Events - Triggered')

            # emit metrics event
            if sleep_count % emit_interval == 0:
                if emit_metrics.is_alive():
                    TraceLogger.error('Skipping Emit Metrics Event, Emit Metrics thread is alive')
                else:
                    emit_metrics = threading.Thread(target=self.emit_metrics, args=(emit_interval,))
                    emit_metrics.start()

            # refresh cluster event
            if sleep_count % refresh_interval == 0:
                if refresh_cluster.is_alive():
                    TraceLogger.error('Skipping Refresh Cluster, Refresh Cluster thread is alive')
                else:
                    refresh_cluster = threading.Thread(target=self.refresh_cluster, args=(refresh_interval,))
                    refresh_cluster.start()

            time.sleep(60)
            sleep_count += 1
