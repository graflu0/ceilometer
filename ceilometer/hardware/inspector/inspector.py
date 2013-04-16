# Main hardware inspector abstraction layering over the hypervisor API.
#


#TODO: update comments
class Inspector(object):

    def inspect_cpus(self, host):
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

    def inspect_netInt(self, host):
        """
        Inspect the network interfaces for a host.

        :param : the target host
        :return: collection with NetIntStats ['name', 'bandwidth', 'used', 'in', 'out', 'error']
        """
        raise NotImplementedError()