# -*- encoding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc
#
# Author: Eoghan Glynn <eglynn@redhat.com>
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
"""Inspector abstraction for read-only access to hypervisors"""

import collections
from ceilometer.openstack.common import log as logging
from pysnmp.entity.rfc3413.oneliner import cmdgen
from ceilometer.hardware.inspector.inspector import Inspector

#TODO: Named to Inspector?

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
# total: Total RAM
# used: Used RAM
# free: Free RAM
#
RAMStats = collections.namedtuple('RAMStats', ['total', 'used'])


# Named tuple representing disk statistics.
#
# description: storage description
# size: storage size (kBytes)
# used: storage used
#
DiskStats = collections.namedtuple('DiskStats',
    ['path', 'size', 'used'])


# Named tuple representing network interface statistics.
#
# name: name of the network interface
# bandwidth: current bandwidth (bit/s)
# received: total number of octets received
# transmitted: total number of octets transmitted
# error: number of outbound packets that could not be transmitted because of errors
#
NetIntStats = collections.namedtuple('NetIntStats',
    ['name', 'bandwidth', 'used', 'received', 'transmitted', 'error'])

# Exception types
#


class InspectorException(Exception):
    def __init__(self, message=None):
        super(InspectorException, self).__init__(message)


class InstanceNotFoundException(InspectorException):
    pass

LOG = logging.getLogger(__name__)

class SNMPInspector(Inspector):

    def __init__(self):
        self._port = 161                             # TODO: Set Port
        self._security_name = "public"
        self._cmdGen = cmdgen.CommandGenerator()

        #CPU OIDs
        self._cpu_1_min_load_oid = "1.3.6.1.4.1.2021.10.1.3.1"
        self._cpu_5_min_load_oid = "1.3.6.1.4.1.2021.10.1.3.2"
        self._cpu_15_min_load_oid = "1.3.6.1.4.1.2021.10.1.3.3"
        #RAM OIDs
        self._ram_total_oid = "1.3.6.1.4.1.2021.4.5.0"
        self._ram_used_oid = "1.3.6.1.4.1.2021.4.6.0"
        #Disk OIDs
        self._disk_index_oid = "1.3.6.1.4.1.2021.9.1.1"
        self._disk_path_oid = "1.3.6.1.4.1.2021.9.1.2"
        self._disk_size_oid = "1.3.6.1.4.1.2021.9.1.6"
        self._disk_used_oid = "1.3.6.1.4.1.2021.9.1.8"
        #Network Interface OIDs
        self._net_int_index_oid = "1.3.6.1.2.1.2.2.1.1"
        self._net_int_name_oid = "1.3.6.1.2.1.2.2.1.2"
        self._net_int_bandwidth_oid = "1.3.6.1.2.1.2.2.1.5"
        self._net_int_received_oid = "1.3.6.1.2.1.2.2.1.10"
        self._net_int_transmitted_oid = "1.3.6.1.2.1.2.2.1.16"
        self._net_int_error_oid = "1.3.6.1.2.1.2.2.1.20"

    def _getValueFromOID(self, oid, ip):
        errorIndication, errorStatus, errorIndex, varBinds = self._cmdGen.getCmd(
            cmdgen.CommunityData(self._security_name),
            cmdgen.UdpTransportTarget((ip, self._port)),
            oid
        )
        if errorIndication:
            LOG.error(errorIndication)
        else:
            if errorStatus:
                LOG.error("%s at %s" % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1] or "?"
                ))
            else:
                for name, val in varBinds:
                    return val

    def _walkOID(self, oid, ip):
        errorIndication, errorStatus, errorIndex, varBindTable = self._cmdGen.getCmd(
            cmdgen.CommunityData(self._security_name),
            cmdgen.UdpTransportTarget((ip, self._port)),
            oid,
            lexicographicMode=False
        )
        if errorIndication:
            LOG.error(errorIndication)
        else:
            if errorStatus:
                LOG.error("%s at %s" % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[int(errorIndex) - 1] or "?"
                ))
            else:
                return varBindTable

    def inspect_cpus(self, host):
        #get 1 minute load
        cpu_1_min_load_Ind = self._getValueFromOID(self._cpu_1_min_load_oid, host.ip_address)

        #get 5 minute load
        cpu_5_min_load_ind = self._getValueFromOID(self._cpu_5_min_load_oid, host.ip_address)

        #get 15 minute load
        cpu_15_min_load_ind = self._getValueFromOID(self._cpu_15_min_load_oid, host.ip_address)

        return CPUStats(cpu1MinLoad=cpu_1_min_load_Ind, cpu5MinLoad=cpu_5_min_load_ind, cpu15MinLoad=cpu_15_min_load_ind)

    def inspect_ram(self, host):
        #get total Ram
        ram_total = self._getValueFromOID(self._ram_total_oid, host.ip_address)

        #get used Ram
        ram_used = self._getValueFromOID(self._ram_used_oid, host.ip_address)

        return RAMStats(total=ram_total, used=ram_used)

    def inspect_disks(self, host):
        disk_indexes = self._walkOID(self._disk_index_oid, host.ip_address)
        disk_stats = []
        for disk_index in disk_indexes:
            disk_path = self._getValueFromOID(self._disk_path_oid + "." + disk_index, host.ip_address)
            disk_size = self._getValueFromOID(self._disk_size_oid + "." + disk_index, host.ip_address)
            disk_used = self._getValueFromOID(self._disk_used_oid + "." + disk_index, host.ip_address)
            disk_stats.append(DiskStats(path=disk_path, size=disk_size, used=disk_used))
        return disk_stats

    def inspect_netInt(self, host):
        net_int_indexes = self._walkOID(self._net_int_index_oid)
        net_int_stats = []
        for net_int_index in net_int_indexes:
            net_int_name = self._getValueFromOID(self._net_int_name_oid + "." + net_int_index, host.ip_address)
            net_int_bandwidth = self._getValueFromOID(self._net_int_bandwidth_oid + "." + net_int_index, host.ip_address)
            net_int_received = self._getValueFromOID(self._net_int_received_oid + "." + net_int_index, host.ip_address)
            net_int_transmitted = self._getValueFromOID(self._net_int_transmitted_oid + "." + net_int_index, host.ip_address)
            net_int_error = self._getValueFromOID(self._net_int_error_oid + "." + net_int_index, host.ip_address)
            net_int_stats.append(NetIntStats(name=net_int_name, bandwidth=net_int_bandwidth, received=net_int_received,
                transmitted=net_int_transmitted, error=net_int_error))
        return net_int_stats