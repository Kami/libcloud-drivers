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
Class used by DIRAC to control virtual machine instances on StratusLab
cloud infrastructures.  This provides just the core interface methods for
DIRAC, the real work is done within the InstanceManagerImpl class.
"""

try:
    from DIRAC import gLogger, S_OK, S_ERROR
except:
    from stratuslab.dirac.DiracMock import gLogger, S_OK, S_ERROR

from stratuslab.dirac import InstanceManagerImpl


class InstanceManager:
    """
    Provides interface for managing virtual machine instances of a
    particular appliance on a StratusLab cloud infrastructure.
    """

    def __init__(self, applianceIdentifier, cloudIdentifier='default'):
        """
        Creates an instance that will manage appliances of a given type
        on a specific cloud infrastructure.  Separate instances must be
        created for different cloud infrastructures and different
        appliances.

        :Parameters:
          **applianceIdentifier** - `string`
            appliance (image) identifier from the StratusLab Marketplace

          **cloudIdentifier** - `string`
            name of the cloud infrastructure to use, defaults to 'default'

        """

        self.log = gLogger.getSubLogger('StratusLab Image %s/%s: ' % (cloudIdentifier, applianceIdentifier))

        self._impl = InstanceManagerImpl.InstanceManagerImpl(applianceIdentifier, cloudIdentifier, 'm1.large')

        self.applianceIdentifier = applianceIdentifier
        self.cloudIdentifier = cloudIdentifier

    def connect(self):
        """
        Tests the connection to the StratusLab cloud infrastructure.  Validates
        the configuration and then makes a request to list active virtual
        machine instances to ensure that the connection works.

        :return: S_OK | S_ERROR
        """

        result = self._impl.check_connection()

        self._logResult(result, 'connect')

        return result

    def startNewInstance(self, vmdiracInstanceID):
        """
        Create a new instance of the given appliance.  If successful, returns
        a tuple with the instance identifier (actually the node object itself)
        and the public IP address of the instance.

        The returned instance identifier (node object) must be treated as an
        opaque identifier for the instance.  It must be passed back to the other
        methods in the class without modification!

        :return: S_OK(node, public_IP) | S_ERROR
        """

        result = self._impl.create(vmdiracInstanceID)

        self._logResult(result, 'startNewInstance')

        return result

    def getInstanceStatus(self, instanceId):
        """
        Given the instance ID, returns the status.

        :Parameters:
          **instanceId** - `string`
            instance ID returned by the create() method, actually a Libcloud node object

        :return: S_OK | S_ERROR
        """

        result = self._impl.status(instanceId)

        self._logResult(result, 'getInstanceStatus: %s' % instanceId)

        return result

    def stopInstance(self, instanceId, public_ip=None):
        """
        Destroys (kills) the given instance.  The public_ip parameter is ignored.

        :Parameters:
          **instanceId** - `string`
            instance ID returned by the create() method, actually a Libcloud node object
          **public_ip** - `string`
            ignored

        :return: S_OK | S_ERROR
        """

        result = self._impl.terminate(instanceId, public_ip)

        self._logResult(result, 'stopInstance: %s' % instanceId)

        return result

    def contextualizeInstance(self, instanceId, public_ip):
        """
        This method is not a regular method in the sense that is not generic at all.
        It will be called only of those VMs which need after-booting contextualisation,
        for the time being, just ssh contextualisation.

        :Parameters:
          **instanceId** - `string`
            instance ID returned by the create() method, actually a Libcloud node object
          **public_ip** - `string`
            public IP of the VM, needed for asynchronous contextualisation


        :return: S_OK(instanceId) | S_ERROR
        """

        result = self._impl.contextualize(instanceId, public_ip)

        self._logResult(result, 'contextualizeInstance: %s, %s' % (instanceId, public_ip))

        return result

    def _logResult(self, result, msg):
        if not result['OK']:
            self.log.error(msg)
            self.log.error(result['Message'])
        else:
            self.log.info('OK: %s' % msg)

