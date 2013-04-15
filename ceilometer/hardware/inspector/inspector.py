# Main virt inspector abstraction layering over the hypervisor API.
#
class Inspector(object):

    def inspect_instances(self):
        """
        List the instances on the current agent.
        """
        raise NotImplementedError()

    def inspect_cpus(self, instance):
        """
        Inspect the CPU statistics for an instance.

        :param instance_name: the name of the target instance
        :return: the number of CPUs and cumulative CPU time
        """
        raise NotImplementedError()

    def inspect_nics(self, instance_name):
        """
        Inspect the NIC statistics for an instance.

        :param instance_name: the name of the target instance
        :return: for each NIC, the number of bytes & packets
                 received and transmitted
        """
        raise NotImplementedError()

    def inspect_disks(self, instance_name):
        """
        Inspect the disk statistics for an instance.

        :param instance_name: the name of the target instance
        :return: list with DiskStats (path, size, used)
        """
        raise NotImplementedError()

    def inspect_ram(self, instance_name):
        """
        Inspect the ram statistics for an instance.

        :param instance_name: the name of the target instance
        :return: total RAM, used RAM
        """
    raise NotImplementedError()