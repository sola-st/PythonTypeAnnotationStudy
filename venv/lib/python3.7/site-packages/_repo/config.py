
import os
from configobj import ConfigObj

class Config(ConfigObj):
    def __init__(self, package_name, **kw):
        self._package_name = package_name
        self._global_ini = os.path.join(
            os.path.expanduser('~'),
            '.' + self._package_name,
            self._package_name + '.ini',
        )
        super(Config, self).__init__(self._global_ini, *kw)

    #def read(self, file_names=None):
    #    if file_names is None and self._package_name:
    #        file_names = [global_ini, self._package_name + '.ini',]
    #    return .read(self, file_names)
