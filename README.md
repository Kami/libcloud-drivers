StratusLab Libcloud Drivers
===========================

This project contains drivers to access StratusLab infrastructures via
Libcloud.  [Libcloud][lc-web] is a python library that allows using a
large number of different cloud infrastructure via a single abstract
API.

*Note that this is alpha-quality code.*  There may be significant bugs
in the implementation and the code itself may change in incompatible
ways without notice.  Use at your own risk!

Building the Code
=================

The software can be built using the standard python distutils.  Do the
following from the top-level directory to create a packaged version of
the code:

```bash
python setup.py sdist
```

A tarball with the code will be created in the dist subdirectory.



[lc-web]: http://libcloud.apache.org/
