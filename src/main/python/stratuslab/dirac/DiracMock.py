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

import logging


class gLogger (object):

    @staticmethod
    def getSubLogger(identifier):
        return gLogger(identifier)

    def __init__(self, identifier):
        self._logger = logging.getLogger(identifier)

    def error(self, msg):
        self._logger.error(msg)

    def info(self, msg):
        self._logger.info(msg)

    def verbose(self, msg):
        self._logger.debug(msg)


def S_ERROR(msg=''):
    return {'OK': False, 'Message': str(msg)}


def S_OK(value=''):
    return {'OK': True, 'Value': value}
