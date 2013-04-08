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
from ceilometer.hardware import instance as hardware_instance
from ceilometer.openstack.common import log
from ceilometer.openstack.common import timeutils

LOG = log.getLogger(__name__)


def _instance_name(instance):
    """Shortcut to get instance name"""
    return getattr(instance, 'OS-EXT-SRV-ATTR:instance_name', None)


def make_counter_from_instance(instance, name, type, unit, volume):
    return counter.Counter(
        name=name,
        type=type,
        unit=unit,
        volume=volume,
        user_id=instance.user_id,
        project_id=instance.tenant_id,
        resource_id=instance.id,
        timestamp=timeutils.isotime(),
        resource_metadata=hardware_instance.get_metadata_from_object(instance),
    )

class CPUPollster(plugin.HardwarePollster):

    LOG = log.getLogger(__name__ + '.cpu')

    utilization_map = {}

    def get_cpu_util(self, instance, cpu_info):
        prev_times = self.utilization_map.get(instance.id)
        self.utilization_map[instance.id] = (cpu_info.time,
                                             datetime.datetime.now())
        cpu_util = 0.0
        if prev_times:
            prev_cpu = prev_times[0]
            prev_timestamp = prev_times[1]
            delta = self.utilization_map[instance.id][1] - prev_timestamp
            elapsed = (delta.seconds * (10 ** 6) + delta.microseconds) * 1000
            cores_fraction = 1.0 / cpu_info.number
            # account for cpu_time being reset when the instance is restarted
            time_used = (cpu_info.time - prev_cpu
                         if prev_cpu <= cpu_info.time else cpu_info.time)
            cpu_util = 100 * cores_fraction * time_used / elapsed
        return cpu_util

    @staticmethod
    def get_counter_names():
        return ['cpu', 'cpu_util']

    def get_counters(self, manager, instance):
        #TODO set instance Attributes
        self.LOG.info('checking instance %s', instance)
        #print(getattr(instance, 'OS-EXT-SRV-ATTR:instance_name', u''))
        #instance_name = _instance_name(instance)
        try:
            cpu_info = manager.inspector_manager.inspect_cpus(instance)
            self.LOG.info("CPUTIME USAGE: %s %d",
                          instance.__dict__, cpu_info.time)
            yield make_counter_from_instance(instance,
                                             name='cpu',
                                             type=counter.TYPE_CUMULATIVE,
                                             unit='ns',
                                             volume=cpu_info.time,
                                             )
        except Exception as err:
            self.LOG.error('could not get CPU time for %s: %s',
                           instance, err)
            self.LOG.exception(err)