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
Driver for StratusLab (http://stratuslab.eu) cloud infrastructures.

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
StratusLabDriver = get_driver(Provider.STRATUSLAB)
driver = StratusLabDriver('default')

driver.list_nodes() #-> []
driver.list_sizes() #-> [<NodeSize: ..., ...]
driver.list_locations() #-> [<NodeLocation: ..., ...]
driver.list_images() #-> [<NodeImage: id=HaFF..., ...]

@note: This driver is currently a prototype.  Use at your own risk!
"""

#
# This code inserts the necessary information into the Libcloud data
# structures so that the StratusLab driver can be found in the usual
# way.  This configuration would be hardcoded into the files types.py
# and providers.py in the libcloud/compute module if the driver were
# distributed as part of Libcloud.
#
# Because this is distributed separately, you must import this class
# BEFORE trying to use the StratusLab driver!
#
from libcloud.compute.types import Provider
from libcloud.compute.providers import DRIVERS

setattr(Provider, 'STRATUSLAB', 'stratuslab')
DRIVERS['stratuslab'] = ('libcloud.compute.drivers.stratuslab_driver', 'StratusLabNodeDriver')


import xml.etree.ElementTree as ET

from stratuslab.Monitor import Monitor
from stratuslab.Runner import Runner
from stratuslab.ConfigHolder import ConfigHolder, UserConfigurator

import stratuslab.Util as StratusLabUtil

import ConfigParser as ConfigParser

import urllib

import uuid
import socket
import struct

from libcloud.common.base import ConnectionKey
from libcloud.compute.base import NodeImage, NodeSize, Node
from libcloud.compute.base import NodeDriver, NodeLocation
from libcloud.compute.types import Provider, NodeState


class StratusLabConnection(ConnectionKey):
    """
    Class currently serves no useful purpose!
    """

    def connect(self, host=None, port=None):
        pass


class StratusLabNodeDriver(NodeDriver):
    """
    StratusLab node driver.
    """

    name = "StratusLab Node Provider"
    website = 'http://stratuslab.eu/'
    type = Provider.STRATUSLAB

    def __init__(self, config_section=None):
        """
        Create an instance of the StratusLabNodeDriver.  All of the
        information for accessing a given StratusLab infrastructure is
        provided in the client configuration file.  The 'credentials'
        here actually refer to the section in the configuration file
        to be used for the 'location'. 

        @param  config_section: Credentials
        @type   config_section: C{str}

        @rtype: C{None}
        """
        self.config_section = config_section

        # TODO: This should raise a ValueError if the given section
        # isn't valid.
        
        # TODO: This should pull out the values for the given section
        # and pass those parameters to the underlying StratusLab
        # API. This will take work on the StratusLab code as well.

        self.connection = StratusLabConnection(self.config_section)


    def get_uuid(self, unique_field=None):
        """

        @param  unique_field: Unique field
        @type   unique_field: C{bool}
        @rtype: L{UUID}
        """
        return str(uuid.uuid4())


    def list_nodes(self):
        """
        List the nodes (machine instances) that are running in the
        location given when initialized.
        """

        config_file = StratusLabUtil.defaultConfigFileUser

        try:
            config = UserConfigurator.configFileToDictWithFormattedKeys(config_file,
                                                                        selected_section=self.config_section)
        except ConfigurationException, ex:
            raise ConfigurationException('Error parsing user configuration file %s' 
                                         % configFile +'. Details: %s' % ex)

        configHolder = ConfigHolder(config=config)
        monitor = Monitor(configHolder)
        vms = monitor.listVms()

        nodes = []
        for vm_info in vms:
            nodes.append(self._vm_info_to_node(vm_info))

        return nodes


    def _vm_info_to_node(self, vm_info):

        attrs = vm_info.getAttributes()
        id = attrs['id'] or None
        name = attrs['deploy_id'] or None
        state = self._to_node_state(attrs['state_summary'] or None)

        public_ip = attrs['template_nic_ip']
        if public_ip:
            public_ips = [public_ip]
        else:
            public_ips = []

        return Node(id,
                    name,
                    state,
                    public_ips,
                    None,
                    self,
                    extra=attrs)


    def _to_node_state(self, state):
        if state:
            state = state.lower()
            if state in ['running', 'epilog']:
                return NodeState.RUNNING
            elif state in ['pending', 'prolog', 'boot']:
                return NodeState.PENDING
            elif state in ['done']:
                return NodeState.TERMINATED
            else:
                return NodeState.UNKNOWN
        else:
            return NodeState.UNKNOWN


    def reboot_node(self, node):
        """
        Reboot the node.  This is not supported by the StratusLab
        cloud.

        @inherits: L{NodeDriver.reboot_node}
        """
        return False


    def destroy_node(self, node):
        """
        Terminate the node and remove it from the node list.  This is
        the equivalent of stratus-kill-instance.
        """
        node.state = NodeState.TERMINATED
        return True


    def list_images(self, location=None):
        """
        Returns a list of images from the StratusLab Marketplace.  The
        image id corresponds to the base64 identifier of the image in
        the Marketplace and the name corresponds to the title (or
        description if title isn't present).

        The location parameter is ignored at the moment and the global
        Marketplace (https://marketplace.stratuslab.eu/metadata) is
        consulted.

        @inherits: L{NodeDriver.list_images}
        """

        # TODO: This should use the configuration file to determine
        # the correct Marketplace URL for the given location.
        return self._get_marketplace_images('https://marketplace.stratuslab.eu/metadata')


    def _get_marketplace_images(self, url):

        images = []
        try:
            filename, _ = urllib.urlretrieve(url)
            tree = ET.parse(filename)
            root = tree.getroot()
            for md in root.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'):
                rdf_desc = md.find('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
                id = rdf_desc.find('{http://purl.org/dc/terms/}identifier').text
                elem = rdf_desc.find('{http://purl.org/dc/terms/}title') or \
                    rdf_desc.find('{http://purl.org/dc/terms/}description')
                if not (elem is None):
                    name = elem.text
                else:
                    name = ''
                images.append(NodeImage(id=id, name=name, driver=self))
        except Exception as e:
            print e

        return images


    def list_sizes(self, location=None):
        """
        Returns a list of predefined node sizes for StratusLab.  These
        are predefined by the StratusLab client and by the client
        configuration.

        @inherits: L{NodeDriver.list_images}
        """

        sizes = []

        # TODO: This should also include types in configuration file.
        machine_types = Runner.getDefaultInstanceTypes()

        for name in machine_types.keys():
            cpu, ram, swap = machine_types[name]
            bandwidth = 1000
            price = 1
            size = NodeSize(id=name,
                            name=name,
                            ram=ram,
                            disk=swap,
                            bandwidth=bandwidth,
                            price=price,
                            driver=self)
            sizes.append(size)

        return sizes


    def list_locations(self):
        """
        Returns a list of StratusLab locations.  These are defined as
        sections in the client configuration file.  The name of each
        location is the name of the section in the configuration
        file.  The country is set to 'ZZ' for all locations for now.

        @inherits: L{NodeDriver.list_locations}
        """

        locations = []

        config_file = StratusLabUtil.defaultConfigFileUser

        parser = ConfigParser.SafeConfigParser()

        try:
            try:
                parser.readfp(config_file) # file
            except AttributeError:
                parser.read(config_file) # filename
        except ConfigParser.ParsingError, ex:
            raise ConfigurationException(ex)

        # TODO: Allow the name and country to be specified in the
        # configuration file.
        for section in parser.sections():
            if not (section in ['instance_types']):
                location = NodeLocation(id=section,
                                        name=section,
                                        country='ZZ',
                                        driver=self)
                locations.append(location)

        return locations


    def create_node(self, **kwargs):
        """
        Creates a node from the given arguments.  This is currently a
        NOOP! 

        @inherits: L{NodeDriver.create_node}
        """
        n = Node(id=l,
                 name='dummy-%d' % l,
                 state=NodeState.RUNNING,
                 public_ips=['127.0.0.%d' % l],
                 private_ips=[],
                 driver=self,
                 size=NodeSize(id='s1', name='foo', ram=2048,
                               disk=160, bandwidth=None, price=0.0,
                               driver=self),
                 image=NodeImage(id='i2', name='image', driver=self),
                 extra={'foo': 'bar'})
        return n


if __name__ == "__main__":
    import doctest

    doctest.testmod()
