# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
import json
import argparse
import configparser

from emitter import ApplicationInsightsEmitter

from exceptions import InvalidConfigurationFileError
from constants import WORKINGDIR


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--emit-interval', type=int, default=5, help='emit interval period in minutes')
    parser.add_argument('--refresh-interval', type=int, default=1440, help='refresh interval period in minutes')

    arguments = parser.parse_args()
    emit_interval, refresh_interval = arguments.emit_interval, arguments.refresh_interval

    try:
        with open(os.path.join(WORKINGDIR, r'appconfig.json')) as file_pointer:
            appconfig = json.load(file_pointer)

        bright_host_ip = appconfig['BrightHostIP']
        instrumentation_key = appconfig['InstrumentationKey']

    except FileNotFoundError:
        raise InvalidConfigurationFileError('Unable to locate app config file.')
    except KeyError:
        raise InvalidConfigurationFileError('Unable to read app config file.')

    try:
        metricsconfig = configparser.RawConfigParser(allow_no_value=True)
        metricsconfig.optionxform = str

        metricsconfig_file_path = os.path.join(WORKINGDIR, r'metricsconfig.ini')
        metricsconfig.read(metricsconfig_file_path)

        metrics = []
        for section in metricsconfig.sections():
            for item in metricsconfig.items(section):
                if item[1] is None:
                    metrics.append(item[0])
    except FileNotFoundError:
        raise InvalidConfigurationFileError('Unable to locate metric config file.')
    except IndexError:
        raise InvalidConfigurationFileError('Unable to read metric config file.')

    emitter = ApplicationInsightsEmitter(bright_host_ip, metrics, instrumentation_key)
    emitter.start(emit_interval, refresh_interval)


if __name__ == '__main__':
    main()
