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
    def __init__(self, global_conf=None):
        self._port = 161                             # Default snmp port
        self._security_name = "public"               # Default security name
        if global_conf:
            if global_conf.get("port"):
                self._port = global_conf.get("port")
            if global_conf.get("securityName"):
                self._security_name = global_conf.get("securityName")

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

    def _get_value_from_oid(self, oid, host):
        errorIndication, errorStatus, errorIndex, varBinds = self._cmdGen.getCmd(
            cmdgen.CommunityData(self._get_security_name(host)),
            cmdgen.UdpTransportTarget((host.ip_address, self._get_port(host))),
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

    def _walk_oid(self, oid, host):
        errorIndication, errorStatus, errorIndex, varBindTable = self._cmdGen.getCmd(
            cmdgen.CommunityData(self._get_security_name(host)),
            cmdgen.UdpTransportTarget((host.ip_address, self._get_port(host))),
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

        def _get_port(self, host):
            port = None
        if host.inspector_configurations.get("snmp"):
            port = host.inspector_configurations.get("snmp").get("port")
        if not port:
            port = self._port
        return port

    def _get_security_name(self, host):
        security_name = None
        if host.inspector_configurations.get("snmp"):
            security_name = host.inspector_configurations.get("snmp").get("securityName")
        if not security_name:
            security_name = self._security_name
        return security_name

    def inspect_cpus(self, host):

        #TODO host.inspector_configurations could be None
#        #get 1 minute load
#        cpu_1_min_load_Ind = self._get_value_from_oid(self._cpu_1_min_load_oid, host)
#
#        #get 5 minute load
#        cpu_5_min_load_ind = self._get_value_from_oid(self._cpu_5_min_load_oid, host)
#
#        #get 15 minute load
#        cpu_15_min_load_ind = self._get_value_from_oid(self._cpu_15_min_load_oid, host)
        test= CPUStats(0,2,5)
        return test
#        return CPUStats(cpu1MinLoad=cpu_1_min_load_Ind, cpu5MinLoad=cpu_5_min_load_ind,
#                        cpu15MinLoad=cpu_15_min_load_ind)

    def inspect_ram(self, host):
        #get total Ram
        ram_total = self._get_value_from_oid(self._ram_total_oid, host)

        #get used Ram
        ram_used = self._get_value_from_oid(self._ram_used_oid, host)

        return RAMStats(total=ram_total, used=ram_used)

    def inspect_disks(self, host):
        disk_indexes = self._walk_oid(self._disk_index_oid, host)
        disk_stats = []
        for disk_index in disk_indexes:
            disk_path = self._get_value_from_oid(self._disk_path_oid + "." + disk_index, host)
            disk_size = self._get_value_from_oid(self._disk_size_oid + "." + disk_index, host)
            disk_used = self._get_value_from_oid(self._disk_used_oid + "." + disk_index, host)
            disk_stats.append(DiskStats(path=disk_path, size=disk_size, used=disk_used))
        return disk_stats

    def inspect_netInt(self, host):
        net_int_indexes = self._walk_oid(self._net_int_index_oid, host)
        net_int_stats = []
        for net_int_index in net_int_indexes:
            net_int_name = self._get_value_from_oid(self._net_int_name_oid + "." + net_int_index, host)
            net_int_bandwidth = self._get_value_from_oid(self._net_int_bandwidth_oid + "." + net_int_index, host)
            net_int_received = self._get_value_from_oid(self._net_int_received_oid + "." + net_int_index, host)
            net_int_transmitted = self._get_value_from_oid(self._net_int_transmitted_oid + "." + net_int_index, host)
            net_int_error = self._get_value_from_oid(self._net_int_error_oid + "." + net_int_index, host)
            net_int_stats.append(NetIntStats(name=net_int_name, bandwidth=net_int_bandwidth, received=net_int_received,
                                 transmitted=net_int_transmitted, error=net_int_error))
        return net_int_stats
