#!/usr/bin/env python
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

from oslo.config import cfg
from stevedore import driver

from ceilometer import agent
from ceilometer import extension_manager
from ceilometer.openstack.common import log

from ceilometer.hardware.virt import inspector as snmp_inspector

OPTS = [
    cfg.ListOpt('disabled_hardware_pollsters',
        default=[],
        help='list of hardware agent pollsters to disable',
    ),
    cfg.StrOpt('hypervisor_inspector',
        default='snmp',
        help='Inspector to use for inspecting hw with snmp'),
    ]

cfg.CONF.register_opts(OPTS)


LOG = log.getLogger(__name__)


class PollingTask(agent.PollingTask):
    def poll_and_publish_instances(self, instances):
        with self.publish_context as publisher:
            for instance in instances:
                if getattr(instance, 'OS-EXT-STS:vm_state', None) != 'error':
                    # TODO(yjiang5) passing counters to get_counters to avoid
                    # polling all counters one by one
                    for pollster in self.pollsters:
                        try:
                            LOG.info("Polling pollster %s", pollster.name)
                            publisher(list(pollster.obj.get_counters(
                                self.manager,
                                instance)))
                        except Exception as err:
                            LOG.warning('Continue after error from %s: %s',
                                pollster.name, err)
                            LOG.exception(err)

    def poll_and_publish(self):
        self.poll_and_publish_instances(
            self.manager.nv.instance_get_all_by_host(cfg.CONF.host))

def get_inspector():
    #inspectors+=getSNMPInspector()
    #inspectors+=getSMARTInspector()
    #inspectors+=...
    #return inspectors
    #TODO siehe oben
    try:
        namespace = 'ceilometer.compute.hardware'
        mgr = driver.DriverManager(namespace,
            'snmp',
            invoke_on_load=True)
        return mgr.driver
    except ImportError as e:
        LOG.error("Unable to load the SNMP inspector: %s" % (e))
        return snmp_inspector.Inspector()

class AgentManager(agent.AgentManager):

    def __init__(self):
        super(AgentManager, self).__init__(
            extension_manager.ActivatedExtensionManager(
                namespace='ceilometer.poll.hardware',
                disabled_names=cfg.CONF.disabled_hardware_pollsters,
            ),
        )
        self._inspectors = get_inspector()

    def create_polling_task(self):
        return PollingTask(self)

    def setup_notifier_task(self):
        """For nova notifier usage"""
        task = PollingTask(self)
        for pollster in self.pollster_manager.extensions:
            task.add(
                pollster,
                self.pipeline_manager.pipelines)
        self.notifier_task = task

    def poll_instance(self, context, instance):
        """Poll one instance."""
        self.notifier_task.poll_and_publish_instances([instance])

    @property
    def inspector(self):
        return self._inspectors