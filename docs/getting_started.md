StratusLab Libcloud Drivers
===========================

This project contains drivers to access StratusLab infrastructures via
Libcloud.  [Libcloud][lc-web] is a python library that allows using a
large number of different cloud infrastructure via a single abstract
API.

Installing the Code
===================

Easy Installation
-----------------

If you've got python installed on your machine with either
`easy_install` or `pip` you can easily install the StratusLab libcloud
driver.

For `easy_install`, just do the following:

```bash
easy_install stratuslab-libcloud-drivers
```

For `pip`, the necessary command is very similar:

```bash
pip install stratuslab-libcloud-drivers
```

Both commands should download and install the driver and Libcloud
itself.

You must also install the StratusLab client.  See below for
instructions. 


Manual Installation
-------------------

You can download the package directly from [PyPi][pypi].  The name of
the package is "stratuslab-libcloud-drivers".  Unwrap the package in a
convenient location and add the root of the unwrapped package to
`PYTHONPATH`.

You must also download and install the Libcloud package and the
StratusLab client, updating the `PYTHONPATH` for those packages as
well.   For the StratusLab client installation, see below.


Installing the StratusLab Client
--------------------------------

The StratusLab command line client must be installed and configured.
See the [StratusLab documentation][sl-docs] for instructions on how to
do this.

In short, you must have a StratusLab client configuration file in the
default location `~/.stratuslab/stratuslab-user.cfg` and the
environmental variable `PYTHONPATH` defined to include the StratusLab
client library.


Using the Driver
================

Once you've downloaded, installed, and configured the necessary
dependencies, you should be able to use the StratusLab driver like
you'd use any other Libcloud driver.  

From the Python interactive shell do the following:

```python
import stratuslab.libcloud.stratuslab_driver
```

This registers the driver with the Libcloud library.  This import must
be done **before** asking Libcloud to use the driver!  Once this is
done, then the driver can be used like any other Libcloud driver.

```python
# Load the driver.
import stratuslab.libcloud.stratuslab_driver

# Obtain an instance of the StratusLab driver. 
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
StratusLabDriver = get_driver(Provider.STRATUSLAB)
driver = StratusLabDriver('default')

# Get the first size, location, and image.
size = driver.list_sizes()[0]
location = driver.list_locations()[0]
image = driver.list_images()[0]

# Run a node through a single lifecycle.
driver.list_nodes()
node = driver.create_node(name='mynode',
     size=size,
     location=location,
     image=image)
driver.list_nodes()
node.destroy()
```

Driver Status
=============

This driver is currently a prototype and of alpha quality.  This
driver should not be used in production.

The driver itself is relatively complete.  The following functions
have working implementations:
* `list_images`: list all valid images in Marketplace
* `list_locations`: list of sections in configuration file
* `list_sizes`: list of standard machine instance types
* `create_node`: start a virtual machine
* `destroy_node`: terminate a virtual machine
* `list_nodes`: list of active virtual machines
* `create_volume`: create persistent disk
* `destroy_volume`: destroy a persistent disk

The following function is specific to the StratusLab driver and is not
part of the Libcloud standard abstraction:
* `list_volumes`: list the available volumes

The following functions have not yet been implemented:
* `attach_volume`
* `detach_volume`

This function will not be implemented as the required functionality is
not provided by a StratusLab cloud:
* `reboot_node`


[lc-web]: http://libcloud.apache.org/
[pypi]: http://pypi.python.org/
[sl-docs]: http://stratuslab.eu/documentation/
