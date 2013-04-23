
import re
from subprocess import Popen, PIPE
import os
import uuid
from ceilometer.openstack.common import log
import socket

LOG = log.getLogger(__name__)

# Exception types
#
class HardwareInstanceException(Exception):
    def __init__(self, message=None):
        super(HardwareInstanceException, self).__init__(message)


class InstanceNotReachableException(HardwareInstanceException):
    pass

class AgentOSNotSupportedException(HardwareInstanceException):
    pass


class HardwareHost(object):

    def __init__(self, ip_address, opts):
        self._ip_address = ip_address
        #TODO: improve getting mac & name
        try:
            self._mac_address = self._get_mac_of_ip(ip_address)
        except InstanceNotReachableException as exception:
            LOG.warning("Instance with IP " +ip_address +" was not reachable")
            LOG.exception(exception)

        #TODO: exception handling
        try:
            self._name=self._get_name_from_ip(ip_address)
        except Exception:
            pass

        self._set_configuration(opts)


    def _get_mac_of_ip(self, ip):
        if (ip.lower() != "localhost") and not(ip.startswith("127.")):
            if (os.name == "posix"):
                try:
                    process = Popen(["ping", "-c","4", ip], stdout=PIPE)
                    process.wait()

                    pid = Popen(["arp", "-n", ip], stdout=PIPE)
                    s = pid.communicate()[0]
                    mac = re.sub(':','',re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s).groups()[0])
                except AttributeError:
                    raise InstanceNotReachableException
            else:
                msg= "Exception while getting MAC address of instance: " +ip +"\n"\
                     +"OS " +os.name +" of hardware agent machine is not supported"
                LOG.warning(msg)
                raise AgentOSNotSupportedException(msg)

        else:
            mac=format(uuid.getnode(), 'x').rjust(12, '0')
        return mac

    def _get_name_from_ip(self, ip):
       return socket.gethostbyaddr(ip)[0]

    def _set_configuration(self, opts):
        if  opts.get("disabled_pollsters") != None:
            self._disabled_pollsters = opts.get("disabled_pollsters")
        else :
            self._disabled_pollsters = []

        #TODO Implement inspectorlist & config
        if opts.get("disabled_inspectors") != None:
            self._disabled_inspectors = opts.get("disabled_inspectors")
        else:
            self._disabled_inspectors = []

        if opts.get("inspector_configuration") != None:
            self._inspector_configurations = opts.get("inspector_configurations")
        else:
            self._inspector_configurations={}

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def name(self):
        return self._name

    @property
    def disabled_pollsters(self):
        return self._disabled_pollsters

    @property
    def disabled_inspectors(self):
        return self.disabled_inspectors

    @property
    def inspector_configuration(self):
        return self._inspector_configuration