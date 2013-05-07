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
"""DESCRIPTION""" #TODO: DESCRIPTION

import copy
import datetime

from ceilometer import counter
from ceilometer.hardware import plugin
from ceilometer.hardware import host as hardware_host
from ceilometer.openstack.common import log
from ceilometer.openstack.common import timeutils

LOG = log.getLogger(__name__)
#TODO: überprüfen ob Disk & Memory Angaben korrekt vom SNMP-Inspector zurückgegeben werden

def make_counter_from_host(host, name, type, unit, volume, res_metadata=None):
    #TODO: Replace user_id and Project_id with real ids
    resource_metadata = dict()
    if(res_metadata is not None):
        metadata = copy.copy(res_metadata)
        resource_metadata = dict(zip(metadata._fields, metadata))
    resource_metadata.update(hardware_host.get_metadata_from_object(host))

    return counter.Counter(
        name=name,
        type=type,
        unit=unit,
        volume=volume,
        user_id='hardware_stuff',
        project_id='hardware_project_tenant_id',
        resource_id=host.id,
        timestamp=timeutils.isotime(),
        resource_metadata=resource_metadata,
    )

class CPUPollster(plugin.HardwarePollster):

    LOG = log.getLogger(__name__ + '.cpu')

    @staticmethod
    def get_counter_names():
        return ['cpu_util_1_min', 'cpu_util_5_min', 'cpu_util_15_min']

    def get_counters(self, manager, host):
        self.LOG.info('checking host %s with id %s', host.ip_address, host.id)
        try:
            cpu_info = manager.inspector_manager.inspect_cpu(host)

            cpu_util_1_min = cpu_info.cpu1MinLoad
            self.LOG.info("CPU UTILIZATION %% last minute: %s %0.2f",
                host.__dict__, cpu_util_1_min)

            cpu_util_5_min = cpu_info.cpu5MinLoad
            self.LOG.info("CPU UTILIZATION %% last 5 minutes: %s %0.2f",
                host.__dict__, cpu_util_5_min)

            cpu_util_15_min = cpu_info.cpu15MinLoad
            self.LOG.info("CPU UTILIZATION %% last 15 minutes: %s %0.2f",
                host.__dict__, cpu_util_15_min)

            yield make_counter_from_host(host,
                name='cpu_util_1_min',
                type=counter.TYPE_GAUGE,
                unit='%',
                volume=cpu_util_1_min,
            )

            yield make_counter_from_host(host,
                name='cpu_util_5_min',
                type=counter.TYPE_GAUGE,
                unit='%',
                volume=cpu_util_5_min,
            )

            yield make_counter_from_host(host,
                name='cpu_util_15_min',
                type=counter.TYPE_GAUGE,
                unit='%',
                volume=cpu_util_15_min,
            )

        except Exception as err:
            self.LOG.error('could not get CPU time for %s with id %s: %s',
                host.ip_address, host.id, err)
            self.LOG.exception(err)

class NetPollster(plugin.HardwarePollster):

    LOG = log.getLogger(__name__ + '.net')

    NET_USAGE_MESSAGE = ' '.join(["NETWORK USAGE:", "%s with id %s and interface %s:", "read-bytes=%d",
                                  "write-bytes=%d"])

    @staticmethod
    def get_counter_names():
        return ['network.bandwidth.bytes',
                'network.incoming.bytes',
                'network.outgoing.bytes',
                'network.outgoing.errors']

    def get_counters(self, manager, host):

        self.LOG.info('checking host %s with id ', host.ip_address, host.id)
        try:
            for nic, info in manager.inspector_manager.inspect_nics(host):
                self.LOG.info(self.NET_USAGE_MESSAGE, host.ip_address, host.id,
                    nic.name, info.rx_bytes, info.tx_bytes)
                yield make_counter_from_host(host,
                    name='network.bandwidth.bytes',
                    type=counter.TYPE_CUMULATIVE,
                    unit='B',
                    volume=info.bandwidth,
                    res_metadata=nic,
                )

                yield make_counter_from_host(host,
                    name='network.incoming.bytes',
                    type=counter.TYPE_CUMULATIVE,
                    unit='B',
                    volume=info.rx_bytes,
                    res_metadata=nic,
                )
                yield make_counter_from_host(host,
                    name='network.outgoing.bytes',
                    type=counter.TYPE_CUMULATIVE,
                    unit='B',
                    volume=info.tx_bytes,
                    res_metadata=nic,
                )
                yield make_counter_from_host(host,
                    name='network.outgoing.errors',
                    type=counter.TYPE_CUMULATIVE,
                    unit='packet',
                    volume=info.error,
                    res_metadata=nic,
                )
        except Exception as err:
            self.LOG.warning('could not get network stats for %s with id %s: %s',
                host.ip_address, host.id, err)
            self.LOG.exception(err)

class DiskSpacePollster(plugin.HardwarePollster):

    LOG = log.getLogger(__name__ + '.diskspace')

    DISKSPACE_USAGE_MESSAGE = ' '.join(["DISKSPACE USAGE:",
                                        "%s with id %s:",
                                        "total space=%d",
                                        "used space=%d",
                                        " on device %s",
                                        " and path %s"
                                        ])

    @staticmethod
    def get_counter_names():
        return ['disk.size.total',
                'disk.size.used']

    def get_counters(self, manager, host):

        try:
            for disk, info in manager.inspector_manager.inspect_diskspace(host):
                self.LOG.info(self.DISKSPACE_USAGE_MESSAGE,
                    host.ip_address, host.id, info.size,
                    info.used, disk.device,
                    disk.path)

            yield make_counter_from_host(host,
                name='disk.size.total',
                type=counter.TYPE_CUMULATIVE,
                unit='B',
                volume=info.size,
                res_metadata=disk
            )

            yield make_counter_from_host(host,
                name='disk.size.used',
                type=counter.TYPE_CUMULATIVE,
                unit='B',
                volume=info.used,
                res_metadata=disk
            )

        except Exception as err:
            self.LOG.warning('could not get disk usage for %s with id %s: %s',
                host.ip_address, host.id, err)
            self.LOG.exception(err)

class MemorySpacePollster(plugin.HardwarePollster):
    LOG = log.getLogger(__name__ + '.memoryspace')

    MEMORYSPACE_USAGE_MESSAGE = ' '.join(["MEMORYSPACE USAGE:",
                                        "%s with id %s:",
                                        "total memory=%d",
                                        "used memory=%d"
                                        ])

    @staticmethod
    def get_counter_names():
        return ['memory.size.total',
                'memory.size.used']

    def get_counters(self, manager, host):

        try:
            memoryinfo = manager.inspector_manager.inspect_memoryspace(host)
            yield make_counter_from_host(host,
                name='memory.size.total',
                type=counter.TYPE_CUMULATIVE,
                unit='B',
                volume=memoryinfo.total
            )
            yield make_counter_from_host(host,
                name='memory.size.used',
                type=counter.TYPE_CUMULATIVE,
                unit='B',
                volume=memoryinfo.used
            )
        except Exception as err:
            self.LOG.warning('could not get memory usage for %s with id %s: %s',
                host.ip_address, host.id, err)
            self.LOG.exception(err)


