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

# Exception types
#
class InspectorException(Exception):
    def __init__(self, message=None):
        super(InspectorException, self).__init__(message)


class InstanceNotFoundException(InspectorException):
    pass


# Main virt inspector abstraction layering over the hypervisor API.
#
class Inspector(object):

    def inspect_instances(self):
        """
        List the instances on the current host.
        """
        raise NotImplementedError()

    def inspect_cpus(self, instance):
        """
        Inspect the CPU statistics for an instance.

        :param instance_name: the name of the target instance
        :return: the number of CPUs and cumulative CPU time
        """
        raise NotImplementedError()

    def inspect_vnics(self, instance_name):
        """
        Inspect the vNIC statistics for an instance.

        :param instance_name: the name of the target instance
        :return: for each vNIC, the number of bytes & packets
                 received and transmitted
        """
        raise NotImplementedError()

    def inspect_disks(self, instance_name):
        """
        Inspect the disk statistics for an instance.

        :param instance_name: the name of the target instance
        :return: for each disk, the number of bytes & operations
                 read and written, and the error count
        """
        raise NotImplementedError()

LOG = logging.getLogger(__name__)

class SNMPInspector(Inspector):

    def __init__(self):
        self.ip = "10.0.0.3"                        #TODO: Set IP (this is a HP SWITCH ProCurve)
        self.port = 161                             #TODO: Set Port
        self.cpuTimeOid = "1.3.6.1.4.1.2021.11.52.0"   #Raw system cpu time, #TODO: Set oids
        self.hrProcessorTableOid = "1.3.6.1.2.1.25.3.3" #hrProcessorTableOid
        self.cmdGen = cmdgen.CommandGenerator()

    def inspect_cpus(self, instance_name):
        #get CPU Load
        errorIndication, errorStatus, errorIndex, varBinds = self.cmdGen.getCmd(
            cmdgen.CommunityData("public"),
            cmdgen.UdpTransportTarget((self.ip, self.port)),
            self.cpuTimeOid
        )
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print("%s at %s" % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or "?"
                ))
            else:
                for name, val in varBinds:
                    self.cpuLoad = val

        #get CPU Count
        errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.getCmd(
            cmdgen.CommunityData("public"),
            cmdgen.UdpTransportTarget((self.ip, self.port)),
            self.hrProcessorTableOid,
            lexicographicMode=False
        )
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print("%s at %s" % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or "?"
                    ))
            else:
                counter = 0
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        counter = counter + 1
                self.cpuNumber = counter/2

        return CPUStats(number=self.cpuNumber, time=self.cpuLoad)
