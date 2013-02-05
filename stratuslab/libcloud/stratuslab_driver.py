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

STRATUSLAB_DRIVER_INDEX = max(DRIVERS.keys()) + 1
DRIVERS[STRATUSLAB_DRIVER_INDEX] = ('stratuslab.libcloud.stratuslab_driver', 'StratusLabNodeDriver')
setattr(Provider, 'STRATUSLAB', STRATUSLAB_DRIVER_INDEX)

import xml.etree.ElementTree as ET

from stratuslab.Monitor import Monitor
from stratuslab.Runner import Runner
from stratuslab.ConfigHolder import ConfigHolder, UserConfigurator
from stratuslab.PersistentDisk import PersistentDisk

import stratuslab.Util as StratusLabUtil

import ConfigParser as ConfigParser

import urllib

import uuid

from libcloud.compute.base import NodeImage, NodeSize, Node
from libcloud.compute.base import NodeDriver, NodeLocation
from libcloud.compute.base import StorageVolume

from libcloud.compute.types import NodeState


#class StratusLabConnection(ConnectionKey):
#    """
#    Class currently serves no useful purpose!
#    """
#
#    def connect(self, host=None, port=None):
#        pass
#

class StratusLabNodeDriver(NodeDriver):
    """
    StratusLab node driver.
    """

    name = "StratusLab Node Provider"
    website = 'http://stratuslab.eu/'
    type = Provider.STRATUSLAB

    default_marketplace_url = 'https://marketplace.stratuslab.eu'

    user_configurator = None
    locations = None
    default_location = None
    sizes = None

    def __init__(self, key, secret=None, secure=False, host=None, port=None,
                 api_version=None, **kwargs):
        """
            Creates a new instance of a StratusLabNodeDriver from the given
            parameters.  All of the parameters are ignored except for the
            ones defined below.

            The configuration is read from the named configuration file (or
            file-like object).  The 'locations' in the API correspond to the
            named sections within the configuration file.

            @param  stratuslab_user_config: File name or file-like object
            from which to read the user's StratusLab configuration.
            Sections in the configuration file correspond to 'locations'
            within this API.
            @type  stratuslab_user_config: C{str} or C{file}

            @param stratuslab_default_location: The id (name) of the section
            within the user configuration file to use as the default location.
            @type  stratuslab_default_location: C{str}

            @rtype: C{StratusLabNodeDriver}
            """
        super(StratusLabNodeDriver, self).__init__(key,
            secret=secret,
            secure=secure,
            host=host,
            port=port,
            api_version=api_version,
            **kwargs)

        user_config_file = kwargs.get('stratuslab_user_config', StratusLabUtil.defaultConfigFileUser)
        default_section = kwargs.get('stratuslab_default_location', 'default')

        self.user_configurator = UserConfigurator(configFile=user_config_file)

        self.locations = self._get_config_locations()
        self.default_location = self.locations.get(default_section, None) or self.locations.get('default')

        self.sizes = self._get_config_sizes()


    def get_uuid(self, unique_field=None):
        """

        @param  unique_field: Unique field
        @type   unique_field: C{bool}
        @rtype: L{UUID}
        """
        return str(uuid.uuid4())


    def _get_config_section(self, location, options={}):
        location = location or self.default_location
        section = location.id

        config = UserConfigurator.userConfiguratorToDictWithFormattedKeys(self.user_configurator,
            selected_section=section)

        configHolder = ConfigHolder(options=options, config=config)
        configHolder.pdiskProtocol = 'https'

        return configHolder


    def _get_config_locations(self):
        """
        Returns a list of StratusLab locations.  These are defined as
        sections in the client configuration file.  The sections may
        contain 'name' and 'country' keys.  If 'name' is not present,
        then the id is also used for the name.  If 'country' is not
        present, then 'unknown' is the default value.
        """

        # TODO: Decide to make parser public or provide method for this info.
        parser = self.user_configurator._parser

        locations = {}

        for section in parser.sections():
            if not (section in ['instance_types']):
                id = section

                try:
                    name = parser.get(section, 'name')
                except ConfigParser.NoOptionError:
                    name = id

                try:
                    country = parser.get(section, 'country')
                except ConfigParser.NoOptionError:
                    country = 'unknown'

                locations[id] = NodeLocation(id=section,
                    name=name,
                    country=country,
                    driver=self)

        return locations


    def _get_config_sizes(self):
        """
        Create all of the node sizes based on the user configuration.
        """

        size_map = {}

        machine_types = Runner.getDefaultInstanceTypes()
        for name in machine_types.keys():
            size = self._create_node_size(name, machine_types[name])
            size_map[name] = size

        machine_types = self.user_configurator.getUserDefinedInstanceTypes()
        for name in machine_types.keys():
            size = self._create_node_size(name, machine_types[name])
            size_map[name] = size

        return size_map.values()


    def _create_node_size(self, name, tuple):
        cpu, ram, swap = tuple
        bandwidth = 1000
        price = 1
        return NodeSize(id=name,
            name=name,
            ram=ram,
            disk=swap,
            bandwidth=bandwidth,
            price=price,
            driver=self)


    def list_nodes(self):
        """
        List the nodes (machine instances) that are running in the
        location given when initialized.
        """

        configHolder = self._get_config_section(self.default_location)

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


    def create_node(self, **kwargs):
        """
        @keyword    name:   String with a name for this new node (required)
        @type       name:   C{str}

        @keyword    size:   The size of resources allocated to this node.
                            (required)
        @type       size:   L{NodeSize}

        @keyword    image:  OS Image to boot on node. (required)
        @type       image:  L{NodeImage}

        @keyword    location: Which data center to create a node in. If empty,
                              undefined behavoir will be selected. (optional)
        @type       location: L{NodeLocation}

        @keyword    auth:   Initial authentication information for the node
                            (optional)
        @type       auth:   L{NodeAuthSSHKey} or L{NodeAuthPassword}

        @return: The newly created node.
        @rtype: L{Node}

        @inherits: L{NodeDriver.create_node}
        """

        name = kwargs.get('name')
        size = kwargs.get('size')
        image = kwargs.get('location')
        location = kwargs.get('location', self.default_location)

        holder = self._get_config_section(location)

        self._insert_required_run_option_defaults(holder)

        # Extract and set size information.
        holder.set('vmCpu', 1)
        holder.set('vmRam', size.ram)
        holder.set('vmSwap', size.disk)

        runner = Runner(image.id, holder)

        ids = runner.runInstance()
        id = ids[0]

        node = Node(id=id,
            name=name,
            state=NodeState.PENDING,
            public_ips=[],
            private_ips=[],
            driver=self,
            size=size,
            image=image,
            extra={'runner': runner})

        try:
            state = runner.getVmState(id)
            node.state = self._to_node_state(state)

            _, ip = runner.getNetworkDetail(id)
            node.public_ips = [ip]

        except Exception as e:
            print e

        # Why does this need to be reset?!
        node.extra = {'runner': runner}

        return node

    def _insert_required_run_option_defaults(self, holder):
        defaults = Runner.defaultRunOptions()

        defaults['verboseLevel'] = 0
        required_options = ['verboseLevel', 'vmTemplateFile',
                            'marketplaceEndpoint', 'vmRequirements',
                            'outVmIdsFile', 'inVmIdsFile']

        for option in required_options:
            if not holder.config.get(option):
                holder.config[option] = defaults[option]


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

        runner = node.extra['runner']
        runner.killInstances([node.id])

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

        location = location or self.default_location

        holder = self._get_config_section(location)
        url = holder.config.get('marketplaceEndpoint', self.default_marketplace_url)
        endpoint = '%s/metadata' % url
        return self._get_marketplace_images(endpoint)


    def _get_marketplace_images(self, url):
        print url
        images = []
        try:
            filename, _ = urllib.urlretrieve(url)
            tree = ET.parse(filename)
            root = tree.getroot()
            for md in root.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'):
                rdf_desc = md.find('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
                id = rdf_desc.find('{http://purl.org/dc/terms/}identifier').text
                elem = rdf_desc.find('{http://purl.org/dc/terms/}title')
                if ((elem is None) or (len(elem) == 0)):
                    elem = rdf_desc.find('{http://purl.org/dc/terms/}description')
                if elem is not None:
                    name = elem.text[:25]
                else:
                    name = ''
                images.append(NodeImage(id=id, name=name, driver=self))
        except Exception as e:
            print e

        return images


    def list_sizes(self, location=None):
        """
        StratusLab node sizes are defined by the client and do not
        depend on the location.  Consequently, the location parameter
        is ignore.  Node sizes defined in the configuration file
        (in the 'instance_types' section) augment or replace the
        standard node sizes defined by default.

        @inherits: L{NodeDriver.list_images}
        """
        return self.sizes


    def list_locations(self):
        """
        Returns a list of StratusLab locations.  These are defined as
        sections in the client configuration file.  The sections may
        contain 'name' and 'country' keys.  If 'name' is not present,
        then the id is also used for the name.  If 'country' is not
        present, then 'unknown' is the default value.

        The returned list and contained NodeLocations are not
        intended to be modified by the user.

        @inherits: L{NodeDriver.list_locations}
        """
        return self.locations.values()


    def list_volumes(self, location=None):
        """
        Creates a list of all of the volumes in the given location.
        This will include private disks of the user as well as public
        disks from other users.

        This method is not a standard part of the Libcloud node driver
        interface.
        """

        configHolder = self._get_config_section(location)

        pdisk = PersistentDisk(configHolder)

        filters = {}
        volumes = pdisk.describeVolumes(filters)

        storage_volumes = []
        for info in volumes:
            storage_volumes.append(self._create_storage_volume(info, location))

        return storage_volumes


    def _create_storage_volume(self, info, location):
        id = info['uuid']
        name = info['tag']
        size = info['size']
        extra = {'location': location}
        return StorageVolume(id, name, size, self, extra=extra)


    def create_volume(self, size, name, location=None, snapshot=None):
        """
        Creates a new storage volume with the given size.  The 'name'
        corresponds to the volume tag.  The visibility of the created
        volume is 'private'.

        The snapshot parameter is currently ignored.

        The created StorageVolume contains a dict for the extra
        information with a 'location' key storing the location used
        for the volume.  This is set to 'default' if no location has
        been given.

        @inherits: L{NodeDriver.create_volume}
        """
        configHolder = self._get_config_section(location)

        pdisk = PersistentDisk(configHolder)

        # Creates a private disk.  Boolean flag = False means private.
        id = pdisk.createVolume(size, name, False)

        extra = {'location': location}

        return StorageVolume(id, name, size, self, extra=extra)


    def destroy_volume(self, volume):
        """
        Destroys the given volume.

        @inherits: L{NodeDriver.destroy_volume}
        """

        # Recover the location (config_section) from the volume.
        # Use the default if not present.
        try:
            location = volume.extra['location']
        except KeyError:
            location = self.default_location

        configHolder = self._get_config_section(location)
        pdisk = PersistentDisk(configHolder)

        id = pdisk.deleteVolume(volume.id)

        return True


if __name__ == "__main__":
    import doctest

    doctest.testmod()
