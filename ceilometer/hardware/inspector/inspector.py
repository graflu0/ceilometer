# Main hardware inspector abstraction layering over the hypervisor API.
#


#TODO: update comments
class Inspector(object):

    def inspect_cpus(self, host):
        """
        Inspect the CPU statistics for an instance.

        :param instance_name: the name of the target instance
        :return: the number of CPUs and cumulative CPU time
        """
        raise NotImplementedError()

    def inspect_disks(self, host):
        """
        Inspect the disk statistics for an instance.

        :param instance_name: the name of the target instance
        :return: collection with DiskStats (path, size, used)
        """
        raise NotImplementedError()

    def inspect_ram(self, host):
        """
        Inspect the ram statistics for a host.

        :param instance_name: the name of the target host
        :return: total RAM, used RAM
        """
        raise NotImplementedError()

    def inspect_netInt(self, host):
        """
        Inspect the network interfaces for a host.

        :param instance_name: the name of the target instance
        :return: collection with NetIntStats ['name', 'bandwidth', 'used', 'in', 'out', 'error']
        """
        raise NotImplementedError()