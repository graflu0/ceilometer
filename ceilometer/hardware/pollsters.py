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


def _host_name(host):
    """Shortcut to get host name"""
    return getattr(host, 'OS-EXT-SRV-ATTR:host', None)


def make_counter_from_host(host, name, type, unit, volume):
    return counter.Counter(
        name=name,
        type=type,
        unit=unit,
        volume=volume,
        user_id=host.user_id,
        project_id=host.tenant_id,
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
        return ['cpu', 'cpu_util']

    def get_counters(self, manager, host):
        #TODO set host Attributes
        self.LOG.info('checking host %s', host.ip_address)
        try:

            cpu_info = manager.inspector_manager.inspect_cpus(host)
#            self.LOG.info("CPUTIME USAGE: %s %d",
#                host.__dict__, cpu_info.time)
#            yield make_counter_from_host(host,
#                                             name='cpu',
#                                             type=counter.TYPE_CUMULATIVE,
#                                             unit='ns',
#                                             volume=cpu_info.time,
#                                             )
        except Exception as err:
            self.LOG.error('could not get CPU time for %s: %s',
                host, err)
            self.LOG.exception(err)