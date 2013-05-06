# Main hardware inspector abstraction layering over the hypervisor API.
#

import collections

# Named tuple representing CPU statistics.
#
# number: number of CPUs
# cpu1MinLoad: 1 minute load
# cpu5MinLoad: 5 minute load
# cpu15MinLoad: 15 minute load
#
CPUStats = collections.namedtuple('CPUStats', ['cpu1MinLoad', 'cpu5MinLoad', 'cpu15MinLoad'])

# Named tuple representing RAM statistics.
#
# total: Total RAM
# used: Used RAM
# free: Free RAM
#
RAMStats = collections.namedtuple('RAMStats', ['total', 'used'])


# Named tuple representing disk statistics.
#
# description: storage description
# size: storage size (kBytes)
# used: storage used
#
DiskStats = collections.namedtuple('DiskStats',
    ['path', 'size', 'used'])


# Named tuple representing an interface.
#
# name: the name of the interface
# mac: the MAC address
#
Interface = collections.namedtuple('Interface', ['name', 'mac'])


# Named tuple representing network interface statistics.
#
# name: name of the network interface
# bandwidth: current bandwidth (bytes/s)
# received: total number of octets received
# transmitted: total number of octets transmitted
# error: number of outbound packets that could not be transmitted because of errors
#
InterfaceStats = collections.namedtuple('InterfaceStats',
    ['bandwidth', 'rx_bytes', 'tx_bytes', 'error'])

class InspectorException(Exception):
    def __init__(self, message=None):
        super(InspectorException, self).__init__(message)

#TODO: update comments
class Inspector(object):

    def inspect_cpu(self, host):
        """
        Inspect the CPU statistics for ahost.

        :param host: the target host
        :return: 1 minute load, 5 minute load, 15 minute load
        """
        raise NotImplementedError()

    def inspect_disks(self, host):
        """
        Inspect the disk statistics for a host.

        :param : the target host
        :return: collection with DiskStats ['path', 'size', 'used']
        """
        raise NotImplementedError()

    def inspect_ram(self, host):
        """
        Inspect the ram statistics for a host.

        :param : the target host
        :return: total RAM, used RAM
        """
        raise NotImplementedError()

    def inspect_network(self, host):
        """
        Inspect the network interfaces for a host.

        :param : the target host
        :return: for each interface, the number of bytes received and transmitted and errors
        """
        raise NotImplementedError()
        
    def set_configuration(self, config):
        raise NotImplementedError()