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
# time: cumulative CPU time
#
CPUStats = collections.namedtuple('CPUStats', ['number', 'time'])

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
        self._ip = "10.0.0.3"                        # TODO: Set IP (this is a HP SWITCH ProCurve)
        self._port = 161                             # TODO: Set Port
        self._securityName = "public"
        self._cmdGen = cmdgen.CommandGenerator()

        #CPU OIDs
        self._cpuTimeOid = "1.3.6.1.4.1.2021.11.52.0"   # Raw system cpu time, # TODO: Set oids
        self._hrProcessorTableOid = "1.3.6.1.2.1.25.3.3.1.2"    # hrProcessorTableOid
        #RAM OIDs
        self._ramTotalOid = "1.3.6.1.4.1.2021.4.5.0"
        self._ramUsedOid = "1.3.6.1.4.1.2021.4.6.0"
        #Disk OIDs
        self._diskIndexOid = "1.3.6.1.4.1.2021.9.1.1"
        self._diskPathOid = "1.3.6.1.4.1.2021.9.1.2"
        self._diskSizeOid = "1.3.6.1.4.1.2021.9.1.6"
        self._diskUsedOid = "1.3.6.1.4.1.2021.9.1.8"
        #Network Interface OIDs
        self._netIntIndexOid = "1.3.6.1.2.1.2.2.1.1"
        self._netIntNameOid = "1.3.6.1.2.1.2.2.1.2"
        self._netIntBandwidthOid = "1.3.6.1.2.1.2.2.1.5"
        self._netIntReceivedOid = "1.3.6.1.2.1.2.2.1.10"
        self._netIntTransmittedOid = "1.3.6.1.2.1.2.2.1.16"
        self._netIntErrorOid = "1.3.6.1.2.1.2.2.1.20"

        self._cpuNumber = -1
        self._cpuTime = -1
        self._ramTotal = -1
        self._ramUsed = -1

    def _getValueFromOID(self, oid):
        errorIndication, errorStatus, errorIndex, varBinds = self._cmdGen.getCmd(
            cmdgen.CommunityData(self._securityName),
            cmdgen.UdpTransportTarget((self._ip, self._port)),
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

    def _walkOID(self, oid):
        errorIndication, errorStatus, errorIndex, varBindTable = self._cmdGen.getCmd(
            cmdgen.CommunityData(self._securityName),
            cmdgen.UdpTransportTarget((self._ip, self._port)),
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

    def inspect_cpus(self, instance):
        #get CPU Load
        self._cpuTime = self._getValueFromOID(self._cpuTimeOid)

        #get CPU Count
        for varBindTableRow in self._walkOID(self._cpuTimeOid):
            for name, val in varBindTableRow:
                self._cpuNumber += 1
        if(self._cpuNumber != -1 and self._cpuTime != -1):
            return CPUStats(number=self._cpuNumber, time=self._cpuTime)

    def inspect_ram(self, instance):
        #get total Ram
        self._ramTotal = self._getValueFromOID(self._ramTotalOid)

        #get used Ram
        self._ramUsed = self._getValueFromOID(self._ramUsedOid)

        if(self._ramTotal != -1 and self._ramUsed != -1):
            return RAMStats(total=self._ramTotal, used=self._ramUsed)

    def inspect_disks(self, instance_name):
        diskIndexes = self._walkOID(self._diskIndexOid)
        diskStats = []
        for diskIndex in diskIndexes:
            pathInd = self._getValueFromOID(self._diskPathOid + "." + diskIndex)
            sizeInd = self._getValueFromOID(self._diskSizeOid + "." + diskIndex)
            usedInd = self._getValueFromOID(self._diskUsedOid + "." + diskIndex)
            diskStats.append(DiskStats(path=pathInd, size=sizeInd, used=usedInd))
        return diskStats

    def inspect_netInt(self, instance_name):
        netIntIndexes = self._walkOID(self._netIntIndexOid)
        netIntStats = []
        for netIntIndex in netIntIndexes:
            nameInd = self._getValueFromOID(self._netIntNameOid + "." + netIntIndex)
            bandwidthInd = self._getValueFromOID(self._netIntBandwidthOid + "." + netIntIndex)
            receivedInd = self._getValueFromOID(self._netIntReceivedOid + "." + netIntIndex)
            transmittedInd = self._getValueFromOID(self._netIntTransmittedOid + "." + netIntIndex)
            errorInd = self._getValueFromOID(self._netIntErrorOid + "." + netIntIndex)
            netIntStats.append(NetIntStats(name=nameInd, bandwidth=bandwidthInd, received=receivedInd,
                transmitted=transmittedInd, error=errorInd))
        return netIntStats