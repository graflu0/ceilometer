from oslo.config import cfg
from stevedore import driver

from ceilometer.openstack.common import log


LOG = log.getLogger(__name__)

from ceilometer.hardware.inspector.snmp import inspector as snmp_inspector

OPTS = [
    cfg.StrOpt('snmp_inspector',
        default='snmp',
        help='Inspector to use for inspecting hw with snmp')
    #TODO add options for new inspectors
    ]

cfg.CONF.register_opts(OPTS)

def get_inspector(inspector_type):
    try:
        namespace = 'ceilometer.hardware.pool'
        mgr = driver.DriverManager(namespace,
            inspector_type,
            invoke_on_load=True)
        return mgr.driver
    except ImportError as e:
        LOG.error("Unable to load the hypervisor inspector: %s" % (e))
        #TODO generalize Inspector
        return snmp_inspector.Inspector()

class InspectorManager(object):

    def __init__(self):
        #TODO add more inspectors
        self._snmp_inspector = get_inspector(cfg.CONF.snmp_inspector)

    def inspect_cpus(self, instance_name):
        #TODO utilize config to check which inspector to take to check this instance
        self._snmp_inspector.inspect_cpus("Test")
        pass