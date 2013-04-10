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

from ceilometer import agent
from ceilometer import extension_manager
from ceilometer.openstack.common import log
from ceilometer.hardware.inspector import manager as inspector_manager
from ceilometer.hardware.instance import HardwareInstance as Instance

OPTS = [
    cfg.ListOpt('disabled_hardware_pollsters',
        default=[],
        help='list of hardware agent pollsters to disable',
    )
    ]

cfg.CONF.register_opts(OPTS)

LOG = log.getLogger(__name__)

class PollingTask(agent.PollingTask):
    def poll_and_publish_instances(self, instances):
        with self.publish_context as publisher:
            for instance in instances:
                for pollster in self.pollsters:
                    try:
                        #TODO get data from instances
                        LOG.info("Polling pollster %s", pollster.name)
                        print(instance)
                        print(list(pollster.obj.get_counters(
                            self.manager,
                            instance)))
                    except Exception as err:
                        LOG.warning('Continue after error from %s: %s',
                            pollster.name, err)
                        LOG.exception(err)

    def poll_and_publish(self):
        """if(self._hosts == None):
            self.hosts = self._get_all_hosts()"""
        self.poll_and_publish_instances(self._get_all_hosts())

    def _get_all_hosts(self):
        #TODO get hosts from cfg, list & return them
        host_ips = ["localhost", "10.0.0.2"]

        hosts =[]

        for host in host_ips:
            hosts.append(Instance(host))

        return hosts

class AgentManager(agent.AgentManager):

    def __init__(self):
        super(AgentManager, self).__init__(
            extension_manager.ActivatedExtensionManager(
                namespace='ceilometer.poll.hardware',
                disabled_names=cfg.CONF.disabled_hardware_pollsters,
            ),
        )
        self._inspector_manager = inspector_manager.InspectorManager()

    def create_polling_task(self):
        return PollingTask(self)

    @property
    def inspector_manager(self):
        return self._inspector_manager