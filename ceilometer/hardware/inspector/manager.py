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

from oslo.config import cfg
from stevedore import driver

from ceilometer.openstack.common import log
from ceilometer.hardware.inspector.snmp import inspector as snmp_inspector
from ceilometer.hardware.inspector import inspector as inspector_interface


LOG = log.getLogger(__name__)



OPTS = [
    cfg.StrOpt('snmp_inspector',
        default='snmp',
        help='Inspector to use for inspecting hw with snmp')
    #TODO add options here for new inspectors
    ]

cfg.CONF.register_opts(OPTS)

class InspectorManager(object):

    def __init__(self, global_conf):
        #TODO add more inspectors
        self._snmp_inspector = self._get_inspector(cfg.CONF.snmp_inspector, global_conf)

    def inspect_cpu(self, host):
        #TODO use config to check which inspector to take to check this host
        return self._snmp_inspector.inspect_cpu(host)

    def inspect_nics(self, host):
        #TODO use config to check which inspector to take to check this host
        return self._snmp_inspector.inspect_network(host)

    def inspect_diskspace(self, host):
        #TODO use config to check which inspector to take to check this host
        return self._snmp_inspector.inspect_diskspace(host)

    def inspect_memoryspace(self, host):
        #TODO use config to check which inspector to take to check this host
        return self._snmp_inspector.inspect_memoryspace(host)

    def _get_inspector(self, inspector_type, global_conf):
        try:
            namespace = 'ceilometer.hardware.inspectors'
            mgr = driver.DriverManager(namespace,
                inspector_type,
                invoke_on_load=True)
            inspector = mgr.driver
            inspector.set_configuration(global_conf.get(cfg.CONF.snmp_inspector))
            return inspector
        except ImportError as e:
            LOG.error("Unable to load the hypervisor inspector: %s" % (e))
            #TODO set configuration
            generic_inspector = inspector_interface.Inspector()
            if(global_conf):
                generic_inspector.set_config(global_conf.get(cfg.CONF.snmp_inspector))
            return generic_inspector