
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


class HardwareInstance(object):
    _ip_address = None
    _mac_address = None
    _name = None

    def __init__(self, ip_address):
        self._ip_address = ip_address
        try:
            self._mac_address = self._get_mac_of_ip(ip_address)
        except InstanceNotReachableException as exception:
            LOG.warning("Instance with IP " +ip_address +" was not reachable")
            LOG.exception(exception)
        #TODO release function get_name_from_ip
        try:
            self._name=self._get_name_from_ip(ip_address)
        except Exception:
            pass


    def _get_mac_of_ip(self, ip):
        if (ip != "localhost") and (ip != "127.0.0.1"):
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
       print(socket.gethostbyaddr("localhost"))

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def name(self):
        return self._name