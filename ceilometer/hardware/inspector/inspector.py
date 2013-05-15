# -*- encoding: utf-8 -*-
#
# Copyright © 2013 ZHAW SoE
#
# Authors: Lucas Graf <graflu0@students.zhaw.ch>
#          Toni Zehnder <zehndton@students.zhaw.ch>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Inspector abstraction for read-only access to hardware components"""

import collections
from ceilometer.plugin import PluginBase

# Named tuple representing CPU statistics.
#
# number: number of CPUs
# cpu1MinLoad: 1 minute load
# cpu5MinLoad: 5 minute load
# cpu15MinLoad: 15 minute load
#
CPUStats = collections.namedtuple('CPUStats', ['cpu1MinLoad', 'cpu5MinLoad', 'cpu15MinLoad'])

# Named tuple representing RAM statistics.
#
# total: Total Memory
# used: Used Memory
# free: Free Memory
#
MemoryStats = collections.namedtuple('MemoryStats', ['total', 'used'])

# Named tuple representing disks.
#
# device: the device name for the disk
#
Disk = collections.namedtuple('Disk', ['device', 'path'])

# Named tuple representing disk statistics.
#
# size: storage size (kBytes)
# used: storage used
#
DiskStats = collections.namedtuple('DiskStats', ['size', 'used'])


# Named tuple representing an interface.
#
# name: the name of the interface
# mac: the MAC address
#
Interface = collections.namedtuple('Interface', ['name', 'mac', 'ip'])


# Named tuple representing network interface statistics.
#
# name: name of the network interface
# bandwidth: current bandwidth (bytes/s)
# received: total number of octets received
# transmitted: total number of octets transmitted
# error: number of outbound packets that could not be transmitted because of errors
#
InterfaceStats = collections.namedtuple('InterfaceStats',
    ['bandwidth', 'rx_bytes', 'tx_bytes', 'error'])

class InspectorException(Exception):
    def __init__(self, message=None):
        super(InspectorException, self).__init__(message)

#TODO: update comments
class Inspector(PluginBase):

    def inspect_cpu(self, host):
        """
        Inspect the CPU statistics for ahost.

        :param host: the target host
        :return: 1 minute load, 5 minute load, 15 minute load
        """
        raise NotImplementedError()

    def inspect_diskspace(self, host):
        """
        Inspect the disk statistics for a host.

        :param : the target host
        :return: for each disk , the size and used space
        """
        raise NotImplementedError()

    def inspect_memoryspace(self, host):
        """
        Inspect the ram statistics for a host.

        :param : the target host
        :return: total memory, used memory
        """
        raise NotImplementedError()

    def inspect_network(self, host):
        """
        Inspect the network interfaces for a host.

        :param : the target host
        :return: for each interface, the number of bytes received and transmitted and errors
        """
        raise NotImplementedError()
        
    def set_configuration(self, config):
        self._config = config