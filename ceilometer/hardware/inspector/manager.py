from oslo.config import cfg
from stevedore import driver

from ceilometer.openstack.common import log
from ceilometer.hardware.inspector.snmp import inspector as snmp_inspector
from ceilometer.hardware.inspector import inspector as inspector_interface


LOG = log.getLogger(__name__)



OPTS = [
    cfg.StrOpt('snmp_inspector',
        default='snmp',
        help='Inspector to use for inspecting hw with snmp')
    #TODO add options here for new inspectors
    ]

cfg.CONF.register_opts(OPTS)

class InspectorManager(object):

    def __init__(self, global_conf):
        #TODO add more inspectors
        self._snmp_inspector = self._get_inspector(cfg.CONF.snmp_inspector, global_conf)

    def inspect_cpus(self, host):
        #TODO use config to check which inspector to take to check this host
        return self._snmp_inspector.inspect_cpus(host)

    def _get_inspector(self, inspector_type, global_conf):
        try:
            namespace = 'ceilometer.hardware.inspectors'
            mgr = driver.DriverManager(namespace,
                inspector_type,
                invoke_on_load=True)
            inspector = mgr.driver
            inspector.set_configuration(global_conf.get(cfg.CONF.snmp_inspector))
            return inspector
        except ImportError as e:
            LOG.error("Unable to load the hypervisor inspector: %s" % (e))
            #TODO set configuration
            generic_inspector = inspector_interface.Inspector()
            if(global_conf):
                generic_inspector.set_config(global_conf.get(cfg.CONF.snmp_inspector))
            return generic_inspector