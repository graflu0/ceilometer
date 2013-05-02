# -*- encoding: utf-8 -*-
#
# Copyright © 2012 eNovance <licensing@enovance.com>
# Copyright © 2012 Red Hat, Inc
#
# Author: Julien Danjou <julien@danjou.info>
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

import copy
import datetime

from ceilometer import counter
from ceilometer.hardware import plugin
from ceilometer.hardware import host as hardware_host
from ceilometer.openstack.common import log
from ceilometer.openstack.common import timeutils

LOG = log.getLogger(__name__)

def make_counter_from_host(host, name, type, unit, volume):
    return counter.Counter(
        name=name,
        type=type,
        unit=unit,
        volume=volume,
        user_id='hardware_stuff',
        project_id='hardware_project',
        resource_id=host.id,
        timestamp=timeutils.isotime(),
        resource_metadata=hardware_host.get_metadata_from_object(host),
    )

class CPUPollster(plugin.HardwarePollster):

    LOG = log.getLogger(__name__ + '.cpu')

    utilization_map = {}

    def get_cpu_util(self, host, cpu_info):
        prev_times = self.utilization_map.get(host.id)
        self.utilization_map[host.id] = (cpu_info.time,
                                             datetime.datetime.now())
        cpu_util = 0.0
        if prev_times:
            prev_cpu = prev_times[0]
            prev_timestamp = prev_times[1]
            delta = self.utilization_map[host.id][1] - prev_timestamp
            elapsed = (delta.seconds * (10 ** 6) + delta.microseconds) * 1000
            cores_fraction = 1.0 / cpu_info.number
            # account for cpu_time being reset when the host is restarted
            time_used = (cpu_info.time - prev_cpu
                         if prev_cpu <= cpu_info.time else cpu_info.time)
            cpu_util = 100 * cores_fraction * time_used / elapsed
        return cpu_util

    @staticmethod
    def get_counter_names():
        return ['cpu_util_1_min', 'cpu_util_5_min', 'cpu_util_15_min']

    def get_counters(self, manager, host):
        #TODO set host Attributes
        self.LOG.info('checking host %s', host.ip_address)
        try:
            cpu_info = manager.inspector_manager.inspect_cpus(host)

            cpu_util_1_min = cpu_info.cpu1MinLoad
            self.LOG.info("CPU UTILIZATION %% last minute: %s %0.2f",
                host.__dict__, cpu_util_1_min)

            cpu_util_5_min = cpu_info.cpu5MinLoad
            self.LOG.info("CPU UTILIZATION %% last minute: %s %0.2f",
                host.__dict__, cpu_util_5_min)

            cpu_util_15_min = cpu_info.cpu15MinLoad
            self.LOG.info("CPU UTILIZATION %% last minute: %s %0.2f",
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
            self.LOG.error('could not get CPU time for %s: %s',
                host, err)
            self.LOG.exception(err)