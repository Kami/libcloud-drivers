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

import copy
import unittest

from stratuslab.dirac.StratusLabEndpointConfiguration import StratusLabEndpointConfiguration
from stratuslab.dirac.DiracMock import gConfig, gConfigHolder

class StratusLabEndpointConfigurationTest(unittest.TestCase):

    def test_empty_config_from_non_existent_path(self):
        cfg = StratusLabEndpointConfiguration('non-existent')
        self.assertEqual(cfg.config(), {})

    def test_defined_path_returns_copy_of_correct_config(self):
        elementName = 'copy_correct'
        path = '%s/%s' % (StratusLabEndpointConfiguration.ENDPOINT_PATH, elementName)
        value = {'a': '1'}
        gConfig.HOLDER.add_options(path, value)

        cfg = StratusLabEndpointConfiguration(elementName)
        self.assertEqual(cfg.config(), value)
        self.assertIsNot(cfg.config(), value)
        self.assertFalse(cfg.validate()['OK'])

    def test_all_required_parameters(self):
        all_keys = StratusLabEndpointConfiguration.DIRAC_REQUIRED_KEYS
        all_keys = all_keys.union(StratusLabEndpointConfiguration.STRATUSLAB_REQUIRED_KEYS)
        value = {}
        for key in all_keys:
            value[key] = key

        elementName = 'all_req_keys'
        path = '%s/%s' % (StratusLabEndpointConfiguration.ENDPOINT_PATH, elementName)
        gConfig.HOLDER.add_options(path, value)

        cfg = StratusLabEndpointConfiguration(elementName)
        self.assertEqual(cfg.config(), value)
        self.assertIsNot(cfg.config(), value)
        self.assertTrue(cfg.validate()['OK'])

    def test_missing_required_parameter(self):
        all_keys = StratusLabEndpointConfiguration.DIRAC_REQUIRED_KEYS
        all_keys = all_keys.union(StratusLabEndpointConfiguration.STRATUSLAB_REQUIRED_KEYS)
        complete = {}
        for key in all_keys:
            complete[key] = key

        for key in all_keys:

            missing = copy.copy(complete)
            del missing[key]

            elementName = 'missing_%s' % key
            path = '%s/%s' % (StratusLabEndpointConfiguration.ENDPOINT_PATH, elementName)
            gConfig.HOLDER.add_options(path, missing)

            cfg = StratusLabEndpointConfiguration(elementName)
            self.assertEqual(cfg.config(), missing)
            self.assertIsNot(cfg.config(), missing)
            self.assertFalse(cfg.validate()['OK'])

    def test_all_parameters(self):
        all_keys = StratusLabEndpointConfiguration.DIRAC_REQUIRED_KEYS
        all_keys = all_keys.union(StratusLabEndpointConfiguration.STRATUSLAB_REQUIRED_KEYS)
        all_keys = all_keys.union(StratusLabEndpointConfiguration.STRATUSLAB_OPTIONAL_KEYS)
        value = {}
        for key in all_keys:
            value[key] = key

        elementName = 'all_keys'
        path = '%s/%s' % (StratusLabEndpointConfiguration.ENDPOINT_PATH, elementName)
        gConfig.HOLDER.add_options(path, value)

        cfg = StratusLabEndpointConfiguration(elementName)
        self.assertEqual(cfg.config(), value)
        self.assertIsNot(cfg.config(), value)
        self.assertTrue(cfg.validate()['OK'])

    def test_invalid_credentials(self):
        all_keys = StratusLabEndpointConfiguration.DIRAC_REQUIRED_KEYS
        all_keys = all_keys.union(StratusLabEndpointConfiguration.STRATUSLAB_REQUIRED_KEYS)
        all_keys = all_keys.union(StratusLabEndpointConfiguration.STRATUSLAB_OPTIONAL_KEYS)
        complete = {}
        for key in all_keys:
            complete[key] = key

        cred_keys = 'ex_username', 'ex_password', 'ex_pem_key', 'ex_pem_certificate'

        for key in cred_keys:

            missing = copy.copy(complete)
            del missing[key]

            elementName = 'invalid_cred_%s' % key
            path = '%s/%s' % (StratusLabEndpointConfiguration.ENDPOINT_PATH, elementName)
            gConfig.HOLDER.add_options(path, missing)

            cfg = StratusLabEndpointConfiguration(elementName)
            self.assertEqual(cfg.config(), missing)
            self.assertIsNot(cfg.config(), missing)
            self.assertFalse(cfg.validate()['OK'])

if __name__ == "__main__":
    unittest.main()

