#
# Copyright (c) 2013, Centre National de la Recherche Scientifique (CNRS)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Provides simple implementations of the DIRAC logging class and the
status functions for use if the DIRAC code is not available.
"""

import copy
import logging


def S_ERROR(msg=''):
    return {'OK': False, 'Message': str(msg)}


def S_OK(value=''):
    return {'OK': True, 'Value': value}


class gConfigHolder (object):

    def __init__(self):
        self.configs = {}

    def set_options(self, configs):
        self.configs = configs

    def add_options(self, key, value):
        self.configs[key] = value

    def get_options(self, cfg_path):
        try:
            return S_OK(self.configs[cfg_path])
        except KeyError:
            return S_ERROR('non-existent path: %s' % cfg_path)


class gConfig (object):

    HOLDER = gConfigHolder()

    @staticmethod
    def getOptionsDict(cfg_path):
        return gConfig.HOLDER.get_options(cfg_path)


class gLogger (object):

    @staticmethod
    def getSubLogger(identifier):
        return gLogger(identifier)

    def __init__(self, identifier):
        self._logger = logging.getLogger(identifier)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def error(self, msg):
        self._logger.error(msg)

    def info(self, msg):
        self._logger.info(msg)

    def verbose(self, msg):
        self._logger.debug(msg)


class EndpointConfiguration(object):

    ENDPOINT_PATH = '/Resources/VirtualMachines/CloudEndpoints'

    def __init__(self):
        self.log = gLogger.getSubLogger(self.__class__.__name__)

    def config(self):
        pass

    def validate(self):
        pass


class ImageConfiguration(object):

    IMAGE_PATH = '/Resources/VirtualMachines/Images'

    def __init__(self, imageElementName):
        self.log = gLogger.getSubLogger(self.__class__.__name__)

        options = gConfig.getOptionsDict('%s/%s' % (self.IMAGE_PATH, imageElementName))

        if not options['OK']:
            self.log.error(options['Message'])
            options = {}
        else:
            options = options['Value']

        # Save a shallow copy of the given dictionary for safety.
        self._options = copy.copy(options)

        # Remove any 'None' mappings from the dictionary.
        for key, value in self._options.items():
            if value is None:
                del self._options[key]

    def config(self):
        return copy.copy(self._options)

    def validate(self):
        return S_OK()


