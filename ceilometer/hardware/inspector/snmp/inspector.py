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

# Named tuple representing instances.
#
# name: the name of the instance
# uuid: the UUID associated with the instance
#
Instance = collections.namedtuple('Instance', ['name', 'UUID'])


# Named tuple representing CPU statistics.
#
# number: number of CPUs
# time: cumulative CPU time
#
CPUStats = collections.namedtuple('CPUStats', ['number', 'time'])


# Named tuple representing disk statistics.
#
# read_bytes: number of bytes read
# read_requests: number of read operations
# write_bytes: number of bytes written
# write_requests: number of write operations
# errors: number of errors
#
DiskStats = collections.namedtuple('DiskStats',
    ['total_size', 'space_available',
     'write_bytes', 'write_requests',
     'errors'])

# Named tuple representing NICs.
#
# name: the name of the NIC
# mac: the MAC address
# fref: the filter ref
# parameters: miscellaneous parameters
#
Interface = collections.namedtuple('Interface', ['name', 'mac',
                                                 'fref', 'parameters'])

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
        self._ip = "10.0.0.3"                        #TODO: Set IP (this is a HP SWITCH ProCurve)
        self._port = 161                             #TODO: Set Port
        self._securityName = "public"
        self._cpuTimeOid = "1.3.6.1.4.1.2021.11.52.0"   #Raw system cpu time, #TODO: Set oids
        self._hrProcessorTableOid = "1.3.6.1.2.1.25.3.3.1.2" #hrProcessorTableOid
        self._cmdGen = cmdgen.CommandGenerator()
        self._cpuNumber = -1
        self._cpuTime = -1

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
                    errorIndex and varBinds[int(errorIndex)-1] or "?"
                    ))
            else:
                for name, val in varBinds:
                    return val

    def _walkOID(self, oid):
        errorIndication, errorStatus, errorIndex, varBindTable = self._cmdGen.getCmd(
            cmdgen.CommunityData("public"),
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
        counter = 0
        for varBindTableRow in self._walkOID(self._cpuTimeOid):
            for name, val in varBindTableRow:
                self.cpuNumber += 1
        if(self._cpuNumber != -1 and self._cpuTime != -1):
            return CPUStats(number=self._cpuNumber, time=self._cpuTime)
