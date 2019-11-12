# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


__all__ = [
    'InvalidConfigurationFileError',
    'BrightClusterConnectionError',
    'EmitMetricsTimeoutError',
    'RefreshClusterTimeoutError'
]


class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidConfigurationFileError(Error):
    """Raised when unable to locate/read configuration file"""
    def __init__(self, *args, **kwargs):
        pass


class BrightClusterConnectionError(Error):
    """Raised when any certificates or private key are not defined or not exist"""
    def __init__(self, *args, **kwargs):
        pass


class EmitMetricsTimeoutError(Error):
    """Raised when Emit Metrics unable to complete the job in given time period"""
    def __init__(self, *args, **kwargs):
        pass


class RefreshClusterTimeoutError(Error):
    """Raised when Refresh Cluster unable to complete the job in given time period"""
    def __init__(self, *args, **kwargs):
        pass
