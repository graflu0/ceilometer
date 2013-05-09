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
import json


LOG = log.getLogger(__name__)



OPTS = [
    cfg.ListOpt('disabled_hardware_inspectors',
        default=[],
        help='list of disabled hardware inspectors'),
    cfg.StrOpt('hardware_inspector_configurations',
        default=None,
        help='dictionary of global hardware inspector configurations'),
    cfg.StrOpt('snmp_inspector',
        default='snmp',
        help='Inspector to use for inspecting hw with snmp')
    #TODO add options here for new inspectors
    ]

cfg.CONF.register_opts(OPTS)

class InspectorManager(object):

    def __init__(self):
        if cfg.CONF.hardware_inspector_configurations is not None :
            global_conf = json.loads(cfg.CONF.hardware_inspector_configurations)
        else:
            global_conf = None

        self._inspectors = {}
        #TODO add entry for inspectors
        self._inspectors[cfg.CONF.snmp_inspector] = self._get_inspector(cfg.CONF.snmp_inspector, global_conf)

        for key in self._inspectors:
            print key

    def inspect_cpu(self, host):
        for key in self._inspectors:
            if key not in cfg.CONF.disabled_hardware_inspectors:
                try:
                    return self._inspectors[cfg.CONF.snmp_inspector].inspect_cpu(host)
                except NotImplementedError:
                    LOG.error("inspect_cpu not implemented in " + key + "inspector")

    def inspect_nics(self, host):
        for key in self._inspectors:
            if key not in cfg.CONF.disabled_hardware_inspectors:
                try:
                    return self._inspectors[cfg.CONF.snmp_inspector].inspect_network(host)
                except NotImplementedError:
                    LOG.error("inspect_cpu not implemented in " + key + " inspector")

    def inspect_diskspace(self, host):
        for key in self._inspectors:
            if key not in cfg.CONF.disabled_hardware_inspectors:
                try:
                    return self._inspectors[cfg.CONF.snmp_inspector].inspect_diskspace(host)
                except NotImplementedError:
                    LOG.error("inspect_cpu not implemented in " + key + " inspector")

    def inspect_memoryspace(self, host):
        for key in self._inspectors:
            if key not in cfg.CONF.disabled_hardware_inspectors:
                try:
                    return self._inspectors[cfg.CONF.snmp_inspector].inspect_memoryspace(host)
                except NotImplementedError:
                    LOG.error("inspect_cpu not implemented in " + key + " inspector")

    def _get_inspector(self, inspector_type, global_conf):
        try:
            namespace = 'ceilometer.hardware.inspectors'
            mgr = driver.DriverManager(namespace,
                inspector_type,
                invoke_on_load=True)
            inspector = mgr.driver
            inspector.set_configuration(global_conf.get(inspector_type))
            return inspector
        except ImportError as e:
            LOG.error("Unable to load the hypervisor inspector: %s" % (e))
            #TODO set configuration
            generic_inspector = inspector_interface.Inspector()
            if(global_conf):
                generic_inspector.set_config(global_conf)
            return generic_inspector