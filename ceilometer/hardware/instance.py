class HardwareInstance(object):

    def __init__(self, ip_address):
        self._ip_address=ip_address
        #TODO get mac adress and
        pass

    @property
    def inspector_manager(self):
        return self._inspector_manager