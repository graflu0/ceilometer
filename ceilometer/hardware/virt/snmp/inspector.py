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
"""Implementation of Inspector abstraction for libvirt"""

from ceilometer.hardware.virt import inspector as snmp_inspector
from ceilometer.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class SNMPInspector(snmp_inspector.Inspector):


    def __init__(self):
        pass

    def inspect_cpus(self, instance_name):
        domain = self._lookup_by_name(instance_name)
        (_, _, _, num_cpu, cpu_time) = domain.info()
        return snmp_inspector.CPUStats(number=2, time=5)