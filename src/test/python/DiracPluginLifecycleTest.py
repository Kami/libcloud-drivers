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
This uses the StratusLab DIRAC plugin to run a virtual machine through
the entire lifecycle.  It requires a configuration file with the real
parameters of a StratusLab cloud infrastructure.  This file is:

src/test/python/cloud-test-params.ini

A reference configuration file is checked into the repository:

src/test/python/cloud-test-params-ref.ini

The configuration file is read during the setup of the test to
initialize the information for the endpoint and image configuration
objects.

NOTE: This test does not do any real clean up of the allocated
cloud resources in the case of failures!  You should release those
resources manually after test failures.
"""

import os
import unittest

from stratuslab.dirac.StratusLabEndpointConfiguration import StratusLabEndpointConfiguration
from stratuslab.dirac.InstanceManager import InstanceManager
from stratuslab.dirac.DiracMock import gConfig, ImageConfiguration

from ConfigParser import SafeConfigParser


class DiracPluginLifecycleTest(unittest.TestCase):

    TEST_PARAMS_FILE = 'cloud-test-params.ini'

    ENDPOINT_ELEMENT = 'stratuslab-endpoint'

    IMAGE_ELEMENT = 'stratuslab-image'

    def setUp(self):

        parser = SafeConfigParser()
        parser.optionxform = lambda option: option # do NOT lowercase keys!
        parser.read(self.TEST_PARAMS_FILE)

        if not os.path.exists(self.TEST_PARAMS_FILE):
            raise Exception('test configuration file missing: %s' % self.TEST_PARAMS_FILE)

        image_params = dict(parser.items('image'))
        image_params['contextConfig'] = dict(parser.items('image_context'))

        path = '%s/%s' % (ImageConfiguration.IMAGE_PATH, self.IMAGE_ELEMENT)
        gConfig.HOLDER.add_options(path, image_params)

        endpoint_params = dict(parser.items('endpoint'))

        path = '%s/%s' % (StratusLabEndpointConfiguration.ENDPOINT_PATH, self.ENDPOINT_ELEMENT)
        gConfig.HOLDER.add_options(path, dict(parser.items('endpoint')))

    def tearDown(self):
        pass

    def test_lifecycle(self):

        im = InstanceManager(self.IMAGE_ELEMENT, self.ENDPOINT_ELEMENT)
        self.assertIsNotNone(im)

        result = im.connect()
        print result
        self.assertTrue(result['OK'])

        result = im.startNewInstance('DiracId-10')
        self.assertTrue(result['OK'])

        node, ip = result['Value']

        result = im.getInstanceStatus(node)
        self.assertTrue(result['OK'])

        result = im.contextualizeInstance(node, ip)
        self.assertTrue(result['OK'])

        result = im.getInstanceStatus(node)
        self.assertTrue(result['OK'])
        self.assertEqual(result['Value'], 'RUNNING')

        result = im.stopInstance(node)
        self.assertTrue(result['OK'])

        result = im.getInstanceStatus(node)
        self.assertTrue(result['OK'])
        self.assertEqual(result['Value'], 'TERMINATED')

if __name__ == "__main__":
    unittest.main()

