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
"""Base class for plugins used by the hardware agent."""

import abc

from ceilometer import plugin


class HardwarePollster(plugin.PollsterBase):
    """Base class for plugins that support the polling API on the
    compute node."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_counters(self, manager, context):
        """Return a sequence of Counter host from polling the
        resources."""
