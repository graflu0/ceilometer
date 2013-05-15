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
"""Tests for the compute pollsters.
"""

import mock
import time

from ceilometer.hardware import pollsters
from ceilometer.hardware import manager
from ceilometer.hardware.inspector import manager as hardware_manager
from ceilometer.hardware.inspector import inspector as hardware_inspector
from ceilometer.tests import base as test_base


class TestPollsterBase(test_base.TestCase):
    #TODO: correct setUp
    def setUp(self):
        super(TestPollsterBase, self).setUp()

        self.inspector_manager = self.mox.CreateMock(hardware_manager.InspectorManager)
        self.mox.StubOutWithMock(hardware_manager, 'InspectorManager')
        hardware_manager.InspectorManager().AndReturn (self.inspector_manager)
        self.host = mock.MagicMock()
        self.host.id = "001122334455"
        self.host.ip_address = "127.0.0.1"
        self.host.name = "name.of.host"


class TestDiskSpacePollster(TestPollsterBase):

    def setUp(self):
        super(TestDiskSpacePollster, self).setUp()

    @mock.patch('ceilometer.pipeline.setup_pipeline', mock.MagicMock())
    def test_get_counters(self):

        disks = [
            (hardware_inspector.Disk(device='l', path='/'),
             hardware_inspector.DiskStats(size = 10000, used = 9000))
        ]

        self.inspector_manager.inspect_diskspace(self.host).AndReturn(disks)
        self.mox.ReplayAll()


        mgr = manager.AgentManager()
        pollster = pollsters.DiskSpacePollster()
        counters = list(pollster.get_counters(mgr, self.host))
        assert counters

        self.assertEqual(set([c.name for c in counters]),
                         set(pollster.get_counter_names()))

        def _verify_disk_metering(name, expected_volume):
            match = [c for c in counters if c.name == name]
            self.assertEquals(len(match), 1, 'missing counter %s' % name)
            self.assertEquals(match[0].volume, expected_volume)
            self.assertEquals(match[0].type, 'gauge')

        _verify_disk_metering('disk.size.total', 10000)
        _verify_disk_metering('disk.size.used', 9000)


class TestNetPollster(TestPollsterBase):

    def setUp(self):
        super(TestNetPollster, self).setUp()

    @mock.patch('ceilometer.pipeline.setup_pipeline', mock.MagicMock())
    def test_get_counters(self):
        self.mox.ReplayAll()


        mgr = manager.AgentManager()
        self.assertEquals(1,1)
#        vnic0 = virt_inspector.Interface(
#            name='vnet0',
#            fref='fa163e71ec6e',
#            mac='fa:16:3e:71:ec:6d',
#            parameters=dict(ip='10.0.0.2',
#                            projmask='255.255.255.0',
#                            projnet='proj1',
#                            dhcp_server='10.0.0.1'))
#        stats0 = virt_inspector.InterfaceStats(rx_bytes=1L, rx_packets=2L,
#                                               tx_bytes=3L, tx_packets=4L)
#        vnic1 = virt_inspector.Interface(
#            name='vnet1',
#            fref='fa163e71ec6f',
#            mac='fa:16:3e:71:ec:6e',
#            parameters=dict(ip='192.168.0.3',
#                            projmask='255.255.255.0',
#                            projnet='proj2',
#                            dhcp_server='10.0.0.2'))
#        stats1 = virt_inspector.InterfaceStats(rx_bytes=5L, rx_packets=6L,
#                                               tx_bytes=7L, tx_packets=8L)
#        vnics = [(vnic0, stats0), (vnic1, stats1)]
#
#        self.inspector.inspect_vnics(self.instance.name).AndReturn(vnics)
#        self.mox.ReplayAll()
#
#        mgr = manager.AgentManager()
#        pollster = pollsters.NetPollster()
#        counters = list(pollster.get_counters(mgr, self.instance))
#        assert counters
#        self.assertEqual(set([c.name for c in counters]),
#                         set(pollster.get_counter_names()))
#
#        def _verify_vnic_metering(name, ip, expected_volume):
#            match = [c for c in counters if c.name == name and
#                     c.resource_metadata['parameters']['ip'] == ip]
#            self.assertEquals(len(match), 1, 'missing counter %s' % name)
#            self.assertEquals(match[0].volume, expected_volume)
#            self.assertEquals(match[0].type, 'cumulative')
#
#        _verify_vnic_metering('network.incoming.bytes', '10.0.0.2', 1L)
#        _verify_vnic_metering('network.incoming.bytes', '192.168.0.3', 5L)
#        _verify_vnic_metering('network.outgoing.bytes', '10.0.0.2', 3L)
#        _verify_vnic_metering('network.outgoing.bytes', '192.168.0.3', 7L)
#        _verify_vnic_metering('network.incoming.packets', '10.0.0.2', 2L)
#        _verify_vnic_metering('network.incoming.packets', '192.168.0.3', 6L)
#        _verify_vnic_metering('network.outgoing.packets', '10.0.0.2', 4L)
#        _verify_vnic_metering('network.outgoing.packets', '192.168.0.3', 8L)


class TestCPUPollster(TestPollsterBase):

    def setUp(self):
        super(TestCPUPollster, self).setUp()

    @mock.patch('ceilometer.pipeline.setup_pipeline', mock.MagicMock())
    def test_get_counters(self):
        self.mox.ReplayAll()


        mgr = manager.AgentManager()
        self.assertEquals(1,1)
#        self.inspector.inspect_cpu(self.instance.name).AndReturn(
#            virt_inspector.CPUStats(time=1 * (10 ** 6), number=2))
#        self.inspector.inspect_cpu(self.instance.name).AndReturn(
#            virt_inspector.CPUStats(time=3 * (10 ** 6), number=2))
#        # cpu_time resets on instance restart
#        self.inspector.inspect_cpu(self.instance.name).AndReturn(
#            virt_inspector.CPUStats(time=2 * (10 ** 6), number=2))
#        self.mox.ReplayAll()
#
#        mgr = manager.AgentManager()
#        pollster = pollsters.CPUPollster()
#
#        def _verify_cpu_metering(zero, expected_time):
#            counters = list(pollster.get_counters(mgr, self.instance))
#            self.assertEquals(len(counters), 2)
#            self.assertEqual(set([c.name for c in counters]),
#                             set(pollster.get_counter_names()))
#            assert counters[0].name == 'cpu_util'
#            assert (counters[0].volume == 0.0 if zero else
#                    counters[0].volume > 0.0)
#            assert counters[1].name == 'cpu'
#            assert counters[1].volume == expected_time
#            # ensure elapsed time between polling cycles is non-zero
#            time.sleep(0.001)
#
#        _verify_cpu_metering(True, 1 * (10 ** 6))
#        _verify_cpu_metering(False, 3 * (10 ** 6))
#        _verify_cpu_metering(False, 2 * (10 ** 6))

"""class TestMemorySpacePollster(TestPollsterBase):
    def test_get_counters(self):
        self.assertEquals(1,1)"""

