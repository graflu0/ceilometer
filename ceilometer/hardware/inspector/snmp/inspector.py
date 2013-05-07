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
"""Inspector for collecting data over SNMP"""


from ceilometer.openstack.common import log as logging
from pysnmp.entity.rfc3413.oneliner import cmdgen
from ceilometer.hardware.inspector import inspector as hardware_inspector

# Exception types
#


class InstanceSNMPEndPointUnreachableException(hardware_inspector.InspectorException):
    pass

LOG = logging.getLogger(__name__)

class SNMPInspector(hardware_inspector.Inspector):
    def __init__(self):
        self._port = 161                             # Default snmp port
        self._security_name = "public"               # Default security name
        self._cmdGen = cmdgen.CommandGenerator()
        #CPU OIDs
        self._cpu_1_min_load_oid = "1.3.6.1.4.1.2021.10.1.3.1"
        self._cpu_5_min_load_oid = "1.3.6.1.4.1.2021.10.1.3.2"
        self._cpu_15_min_load_oid = "1.3.6.1.4.1.2021.10.1.3.3"
        #Memory OIDs
        self._memory_total_oid = "1.3.6.1.4.1.2021.4.5.0"
        self._memory_used_oid = "1.3.6.1.4.1.2021.4.6.0"
        #Disk OIDs
        self._disk_index_oid = "1.3.6.1.4.1.2021.9.1.1"
        self._disk_path_oid = "1.3.6.1.4.1.2021.9.1.2"
        self._disk_device_oid = "1.3.6.1.4.1.2021.9.1.3"
        self._disk_size_oid = "1.3.6.1.4.1.2021.9.1.6"
        self._disk_used_oid = "1.3.6.1.4.1.2021.9.1.8"
        #Network Interface OIDs
        self._interface_index_oid = "1.3.6.1.2.1.2.2.1.1"
        self._interface_name_oid = "1.3.6.1.2.1.2.2.1.2"
        self._interface_bandwidth_oid = "1.3.6.1.2.1.2.2.1.5"
        self._interface_mac_oid = "1.3.6.1.2.1.2.2.1.6"
        self._interface_ip_oid = "1.3.6.1.2.1.4.20.1.2"
        self._interface_received_oid = "1.3.6.1.2.1.2.2.1.10"
        self._interface_transmitted_oid = "1.3.6.1.2.1.2.2.1.16"
        self._interface_error_oid = "1.3.6.1.2.1.2.2.1.20"

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
        errorIndication, errorStatus, errorIndex, varBindTable = self._cmdGen.nextCmd(
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
                    errorIndex and varBindTable[int(errorIndex) - 1] or "?"
                    ))
            else:
                return varBindTable

    def inspect_cpu(self, host):

        #get 1 minute load
        cpu_1_min_load_ind = self._get_value_from_oid(self._cpu_1_min_load_oid, host)

        #get 5 minute load
        cpu_5_min_load_ind = self._get_value_from_oid(self._cpu_5_min_load_oid, host)

        #get 15 minute load
        cpu_15_min_load_ind = self._get_value_from_oid(self._cpu_15_min_load_oid, host)

        return hardware_inspector.CPUStats(cpu1MinLoad=str(cpu_1_min_load_ind), cpu5MinLoad=str(cpu_5_min_load_ind),
                        cpu15MinLoad=str(cpu_15_min_load_ind))

    def inspect_memory(self, host):
        #get total memory
        total = self._get_value_from_oid(self._memory_total_oid, host)

        #get used memory
        used = self._get_value_from_oid(self._memory_used_oid, host)

        return hardware_inspector.MemoryStats(total=total, used=used)

    def inspect_diskspace(self, host):
        disks = self._walk_oid(self._disk_index_oid, host)

        for disk in disks:
            for object_name, value in disk:

                path = self._get_value_from_oid(self._disk_path_oid + "." + str(value), host)
                device = self._get_value_from_oid(self._disk_device_oid + "." + str(value), host)
                size = self._get_value_from_oid(self._disk_size_oid + "." + str(value), host)
                used = self._get_value_from_oid(self._disk_used_oid + "." + str(value), host)

                disk = hardware_inspector.Disk(device=device, path=path)
                stats = hardware_inspector.DiskStats(size=size,used=used)

                yield (disk, stats)


    def inspect_network(self, host):
        net_interfaces = self._walk_oid(self._interface_index_oid, host)

        for interface in net_interfaces:
            for object_name, value in interface:
                ip = self._get_ip_for_interface(host, value)
                if not ip.startswith("127."):
                    name = self._get_value_from_oid(self._interface_name_oid + "." + str(value), host)
                    mac = self._get_value_from_oid(self._interface_mac_oid + "." + str(value), host)
                    bandwidth = self._get_value_from_oid(self._interface_bandwidth_oid + "." + str(value), host)/8 # bits/s to byte/s
                    rx_bytes = self._get_value_from_oid(self._interface_received_oid + "." + str(value), host)
                    tx_bytes = self._get_value_from_oid(self._interface_transmitted_oid + "." + str(value), host)
                    error = self._get_value_from_oid(self._interface_error_oid + "." + str(value), host)

                    interface = hardware_inspector.Interface(name=str(name),mac=':'.join(['%x' % ord(x) for x in mac]), ip=str(ip))
                    stats = hardware_inspector.InterfaceStats(bandwidth=str(bandwidth),rx_bytes=str(rx_bytes),
                                                              tx_bytes=str(tx_bytes),error=str(error))

                    yield (interface, stats)

    def set_configuration(self, config):
        self._config = config

    def _get_port(self, host):
        if host.inspector_configurations and host.inspector_configurations.get("snmp") and host.inspector_configurations.get("snmp").get("port"):
            port = host.inspector_configurations.get("snmp").get("port")
        elif self._config and self._config.get("port"):
            port = self._config.get("port")
        else:
            port = self._port
        return port

    def _get_security_name(self, host):
        if host.inspector_configurations and host.inspector_configurations.get("snmp") and host.inspector_configurations.get("snmp").get("securityName"):
            security_name = host.inspector_configurations.get("snmp").get("securityName")
        elif self._config and self._config.get("securityName"):
            security_name = self._config.get("securityName")
        else:
            security_name = self._security_name
        return security_name

    def _get_ip_for_interface(self, host, interface_id):
        ip_addresses = self._walk_oid(self._interface_ip_oid, host)
        for ip in ip_addresses:
            for object_name, value in ip:
                if value == interface_id:
                    return object_name.__str__().replace(self._interface_ip_oid+".","")
