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
"""Manage the inspectors and calls them"""

from oslo.config import cfg
from stevedore import driver

from ceilometer.openstack.common import log
from ceilometer import extension_manager
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
    ]

cfg.CONF.register_opts(OPTS)

class InspectorManager(object):

    def __init__(self):

        if cfg.CONF.hardware_inspector_configurations is not None :
            global_conf = json.loads(cfg.CONF.hardware_inspector_configurations)
        else:
            global_conf = {}
        self._inspectors = {}
        for name in list(extension_manager.ActivatedExtensionManager(
                        namespace='ceilometer.hardware.inspectors',
                        disabled_names=cfg.CONF.disabled_hardware_inspectors,).names()):
            self._inspectors[name] = self._get_inspector(name, global_conf)

    def inspect_cpu(self, host):
        for key in self._inspectors:
            try:
                if key not in host.disabled_inspectors:
                    return self._inspectors[key].inspect_cpu(host)
            except NotImplementedError:
                LOG.error("inspect_cpu not implemented in " + key + "inspector")

    def inspect_nics(self, host):
        for key in self._inspectors:
            try:
                if key not in host.disabled_inspectors:
                    return self._inspectors[key].inspect_network(host)
            except NotImplementedError:
                LOG.error("inspect_cpu not implemented in " + key + " inspector")

    def inspect_diskspace(self, host):
        for key in self._inspectors:
            try:
                if key not in host.disabled_inspectors:
                    return self._inspectors[key].inspect_diskspace(host)
            except NotImplementedError:
                LOG.error("inspect_cpu not implemented in " + key + " inspector")


    def inspect_memoryspace(self, host):
        for key in self._inspectors:
            try:
                if key not in host.disabled_inspectors:
                    return self._inspectors[key].inspect_memoryspace(host)
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
            generic_inspector = inspector_interface.Inspector()
            if(global_conf):
                generic_inspector.set_config(global_conf)
            return generic_inspector