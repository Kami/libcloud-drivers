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
Detailed implementation of the StratusLab InstanceManager.  Uses
Libcloud API to connect to the StratusLab services.
"""

import os

# ensures that StratusLab Libcloud driver is loaded before use
from libcloud.compute.providers import set_driver

set_driver('STRATUSLAB',
           'stratuslab.libcloud.stratuslab_driver',
           'StratusLabNodeDriver')

from libcloud.compute.base import NodeAuthSSHKey
from libcloud.compute.providers import get_driver

try:
    from DIRAC import gLogger, S_OK, S_ERROR
except:
    from stratuslab.dirac.Mock import gLogger, S_OK, S_ERROR


class InstanceManagerImpl (object):
    """ Implementation of the InstanceManager functionality. """

    def __init__(self, applianceIdentifier, cloudIdentifier='default', sizeIdentifier='m1.large'):
        """
        Initializes this class with the applianceIdentifier (Stratuslab Marketplace
        image identifier), the cloud infrastructure, and the resource requirements
        (size) of the instances.

        NOTE: This constructor will raise an exception if there is a problem with
        any of the configuration, either when creating the Libcloud driver or with
        the given parameters.

        :Parameters:
          **applianceIdentifier** - `string`
            appliance (image) identifier from the Marketplace
          **cloudIdentifier** - `string`
            name of cloud infrastructure ('location' in Libcloud)
          **sizeIdentifier** - `string`
            name of the machine type (resource definition) to use

        """

        self.log = gLogger.getSubLogger(self.__class__.__name__)

        # Obtain instance of StratusLab driver.
        StratusLabDriver = get_driver('stratuslab')
        self._driver = StratusLabDriver('unused-key')

        self.image = self._get_image(applianceIdentifier)
        self.location = self._get_location(cloudIdentifier)
        self.size = self._get_size(sizeIdentifier)

        self._validate_configuration()

    def check_connection(self):
        """
        Checks the connection by trying to list the running machine instances (nodes).
        Note that listing the running nodes is not a standard Libcloud function.

        :return: S_OK | S_ERROR
        """

        try:
            _ = self._driver.list_nodes()
            return S_OK()
        except Exception, errmsg:
            return S_ERROR(errmsg)

    def create(self, vmdiracInstanceID=''):
        """
        This creates a new virtual machine instance based on the appliance identifier
        and cloud identifier defined when this object was created.

        Successful creation returns a tuple with the node object returned from the
        StratusLab Libcloud driver and the public IP address of the instance.

        NOTE: The node object should be treated as an opaque identifier by the
        called and returned unmodified when calling the other methods of this class.

        :return: S_OK( ( node, publicIP ) ) | S_ERROR
        """

        # Get ssh key.
        home = os.path.expanduser('~')
        ssh_public_key_path = os.path.join(home, '.ssh', 'id_dsa.pub')

        with open(ssh_public_key_path) as f:
            pubkey = NodeAuthSSHKey(f.read())

        # Create the new instance, called a 'node' for Libcloud.
        try:
            self.node = self._driver.create_node(name=vmdiracInstanceID,
                                                 size=self.size,
                                                 location=self.location,
                                                 image=self.image,
                                                 auth=pubkey)
        except Exception, e:
            self.node = None
            return S_ERROR(e)

        return S_OK((self.node, self.node.public_ip[0]))

    def status(self, node):
        """
        Return the state of the given node.  This converts the Libcloud states (0-4)
        to their DIRAC string equivalents.  Note that this is not a reversible mapping.

        :Parameters:
          **node** - `string`
            node object returned from the StratusLab Libcloud driver

        :return: S_OK( status ) | S_ERROR
        """

        state = node.state

        # reversed from libcloud
        STATE_MAP = {0: 'RUNNING',
                     1: 'REBOOTING',
                     2: 'TERMINATED',
                     3: 'PENDING',
                     4: 'UNKNOWN'}

        if not state in STATE_MAP:
            return S_ERROR('invalid node state (%s) detected' % state)

        return S_OK(STATE_MAP[state])

    def terminate(self, node, public_ip=''):
        """
        Terminates the node with the given instanceId.

        :Parameters:
          **node** - `node`
            node object returned from the StratusLab Libcloud driver
          **public_ip** - `string`
            parameter is ignored

        :return: S_OK | S_ERROR
        """

        try:
            if node:
                node.destroy()
            return S_OK()
        except Exception, e:
            return S_ERROR(e)

    def contextualize(self, node, public_ip):
        """
        Contextualize the given instance.  This is currently a no-op.

        This must return S_OK(instanceId) on success!

        :Parameters:
          **node** - `node`
            node object returned from the StratusLab Libcloud driver
          **public_ip** - `string`
            public IP assigned to the node if any

        :return: S_OK(instanceId) | S_ERROR
        """

        # No-op for now.
        pass

    def _validate_configuration(self):
        if self.image is None:
            raise Exception('invalid appliance identifier')
        if self.location is None:
            raise Exception('invalid cloud identifier')
        if self.size is None:
            raise Exception('invalid size identifier')

    def _get_location(self, cloudIdentifier):
        locations = self._driver.list_locations()
        return S_OK([location for location in locations if location.name == cloudIdentifier])

    def _get_image(self, applianceIdentifier):
        images = self._driver.list_images()
        return S_OK([image for image in images if image.id == applianceIdentifier])

    def _get_size(self, sizeIdentifier):
        sizes = self._driver.list_sizes()
        return S_OK([size for size in sizes if size.id == sizeIdentifier])
