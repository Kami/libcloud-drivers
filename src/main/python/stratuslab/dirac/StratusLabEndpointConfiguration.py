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

try:
    from DIRAC import gConfig, gLogger, S_OK, S_ERROR
    from VMDIRAC.WorkloadManagementSystem.Utilities.Configuration import EndpointConfiguration
except:
    from stratuslab.dirac.DiracMock import gConfig, gLogger, S_OK, S_ERROR
    from stratuslab.dirac.DiracMock import EndpointConfiguration

import copy


class StratusLabEndpointConfiguration(EndpointConfiguration):
    """
    Class that parses the <stratusLabEndpoint> section of the configuration and
    formats this configuration as a dictionary.
    """

    DIRAC_REQUIRED_KEYS = frozenset(['vmPolicy', 'vmStopPolicy', 'cloudDriver',
                                     'siteName', 'maxEndpointInstances'])

    STRATUSLAB_REQUIRED_KEYS = frozenset(['ex_endpoint'])

    STRATUSLAB_OPTIONAL_KEYS = frozenset(['ex_name', 'ex_country',
                                          'ex_pdisk_endpoint', 'ex_marketplace_endpoint',
                                          'ex_username', 'ex_password', 'ex_pem_key', 'ex_pem_certificate',
                                          'ex_user_ssh_private_key', 'ex_user_ssh_public_key'])

    def __init__(self, stratuslabEndpoint):
        """
        Constructor directly reads the named stratuslabEndpoint section
        in the configuration.

        :Parameters:
          **stratuslabEndpoint** - `string`
            name of the element containing the configuration for a StratusLab cloud
        """

        super(StratusLabEndpointConfiguration, self).__init__()

        options = gConfig.getOptionsDict('%s/%s' % (self.ENDPOINT_PATH, stratuslabEndpoint))

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

        cfg = self.config()

        defined_keys = frozenset(cfg.keys())

        all_required_keys = self.DIRAC_REQUIRED_KEYS.union(self.STRATUSLAB_REQUIRED_KEYS)
        all_keys = all_required_keys.union(self.STRATUSLAB_OPTIONAL_KEYS)

        missing_keys = all_required_keys.difference(defined_keys)
        if missing_keys:
            return S_ERROR('Missing mandatory keys for StratusLab endpoint configuration: %s' % str(missing_keys))

        unknown_keys = defined_keys.difference(all_keys)
        if unknown_keys:
            return S_ERROR('Unknown keys in StratusLab endpoint configuration: %s' % unknown_keys)

        # username and password must either both be defined or both be undefined
        credential_keys = frozenset(['ex_username', 'ex_password'])
        defined_credential_keys = defined_keys.intersection(credential_keys)
        if not (len(defined_credential_keys) == 0 or len(defined_credential_keys) == 2):
            return S_ERROR('the keys "%s" must be both defined or both undefined' % credential_keys)

        # same for the user's certificate and key
        credential_keys = frozenset(['ex_pem_key', 'ex_pem_certificate'])
        defined_credential_keys = defined_keys.intersection(credential_keys)
        if not (len(defined_credential_keys) == 0 or len(defined_credential_keys) == 2):
            return S_ERROR('the keys "%s" must be both defined or both undefined' % credential_keys)

        self.log.info('*' * 50)
        self.log.info('StratusLab Endpoint Configuration')
        for key, value in sorted(cfg.iteritems()):
            if key != 'ex_password':
                self.log.info('%s : %s' % (key, value))
            else:
                self.log.info('%s : ********' % key)
        self.log.info('*' * 50)

        return S_OK()
