StratusLab Libcloud Drivers
===========================

This project contains drivers to access StratusLab infrastructures via
Libcloud.  [Libcloud][lc-web] is a python library that allows using a
large number of different cloud infrastructure via a single abstract
API.

Installing the Code
===================

The code is intended to be installed with pip.  You should be able to
simply do the following:

```bash
pip install stratuslab-libcloud-drivers
```

If this is a system-wide installation, then the PYTHONPATH and PATH
should already be set correctly.  If it is a local installation, you
may need to set these variables by hand.

You can download the package directly from [PyPi][pypi].  The name of
the package is "stratuslab-libcloud-drivers".  The "apache-libcloud"
and "stratuslab-client" packages along with their dependencies are
also required.  Using pip is very strongly recommended.


Configuring the StratusLab Client
=================================

The StratusLab command line client must be configured.  Use the
command `stratus-copy-config` to copy an example configuration file
into place.  The command will print the location of your configuration
file.  The example configuration file contains extensive documentation
on the parameters.  Edit the file and put in your credentials and
cloud endpoints.

More detailed documentation can be found in the [StratusLab
documentation][sl-docs] area on the website.


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
size = driver.list_sizes().pop()
location = driver.list_locations().pop()
image = driver.list_images().pop()

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
driver should _not_ be used in production.

The driver is functionally complete, but may not work with all of the
typical libcloud workflows.  These will be verified as tests are added
to the code base.

In detail, the following functions have working implementations:
* `list_images`: list all valid images in Marketplace
* `list_locations`: list of sections in configuration file
* `list_sizes`: list of standard machine instance types
* `create_node`: start a virtual machine
* `destroy_node`: terminate a virtual machine
* `list_nodes`: list of active virtual machines
* `create_volume`: create persistent disk
* `destroy_volume`: destroy a persistent disk
* `attach_volume`: attach a volume to node
* `detach_volume`: remove a volume from a node

The following function is specific to the StratusLab driver and is not
part of the Libcloud standard abstraction:
* `list_volumes`: list the available volumes

This function will not be implemented as the required functionality is
not provided by a StratusLab cloud:
* `reboot_node`

[lc-web]: http://libcloud.apache.org/
[pypi]: http://pypi.python.org/
[sl-docs]: http://stratuslab.eu/documentation/
