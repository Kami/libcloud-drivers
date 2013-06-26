#!/usr/bin/env python

from stratuslab.dirac.InstanceManager import InstanceManager

im = InstanceManager('BN1EEkPiBx87_uLj2-sdybSI-Xb', 'lal')

result = im.connect()

if not result['OK']:
    raise Exception('error connecting to cloud')

result = im.startNewInstance('dummy')

if not result['OK']:
    raise Exception('cannot start instance')

node, ip = result['Value']

result = im.getInstanceStatus(node)

if not result['OK']:
    raise Exception('error getting instance status')

result = im.contextualizeInstance(node, 'ignored')

if not result['OK']:
    raise Exception('error contextualizing instance')

result = im.getInstanceStatus(node)

if result['Value'] != 'RUNNING':
    raise Exception('instance in unexpected state; expected RUNNING')

result = im.stopInstance(node)

if not result['OK']:
    raise Exception('error stopping instance')

result = im.getInstanceStatus(node)

if not result['OK']:
    raise Exception('error getting instance status after stop')

if result['Value'] != 'TERMINATED':
    raise Exception('instance in unexpected state; expected TERMINATED')

