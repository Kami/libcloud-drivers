StratusLab Libcloud Drivers
===========================

This project contains drivers to access StratusLab infrastructures via
Libcloud.  [Libcloud][lc-web] is a python library that allows using a
large number of different cloud infrastructure via a single abstract
API.

Building the Code
=================

The software can be built using the standard python utilities:
distutils.

Do the following from the top-level directory to create a packaged
version of the code:

```bash
python setup.py sdist
```

A tarball with the code will be created in the dist subdirectory.

Prerequisites
=============

StratusLab Client
-----------------

The StratusLab command line client must be installed and configured.
See the [StratusLab documentation][sl-docs] for instructions on how to do this.

In short, you must have a StratusLab client configuration file in the
default location `~/.stratuslab/stratuslab-user.cfg` and the
environmental variable `PYTHONPATH` defined to include the StratusLab
client library.


Libcloud
--------

The Libcloud library must also be installed.  It can be obtained from
[PyPi][pypi] and installed in the usual ways.


Using the Driver
================

The StratusLab Libcloud driver is currently neither included in the
Libcloud distribution nor available from PyPi.  You must build
checkout this repository and then build the distribution packages or
use the checked out version directly.

To use the checked out version directly, just add the root of the
directory to the `PYTHONPATH` variable.

Before using the StratusLab Libcloud driver you need to tell Libcloud
where to find the driver.

Do the following:

```python
import lcsl.compute.drivers.stratuslab_driver
```

This import must be done **before** asking Libcloud to load the
driver!  Once this is done, then the driver can be used like any other
Libcloud driver.

```python
>>> from libcloud.compute.types import Provider
>>> from libcloud.compute.providers import get_driver
>>> StratusLabDriver = get_driver(Provider.STRATUSLAB)
>>> driver = StratusLabDriver('default')
>>> 
>>> driver.list_locations()
#[<NodeLocation: id=default, name=default, country=ZZ, driver=StratusLab Node Provider>,
# <NodeLocation: id=test, name=test, country=ZZ, driver=StratusLab Node Provider>]
```

The list functions have simple prototype implementations:
* `list_images`: list all valid images in Marketplace
* `list_locations`: list of sections in configuration file
* `list_sizes`: list of standard machine instance types
* `create_node`: start a virtual machine
* `destroy_node`: terminate a virtual machine
* `list_nodes`: list of active virtual machines
* `create_volume`: create persistent disk
* `destroy_volume`: destroy a persistent disk
* `list_volumes`: list the available volumes (not part of Libcloud API)

These functions haven't yet been implemented:
* `reboot_node`: not supported by StratusLab cloud
* `attach_volume`
* `detach_volume`


[lc-web]: http://libcloud.apache.org/
[sl-docs]: http://stratuslab.eu/documentation/
[pypi]: http://pypi.python.org/
