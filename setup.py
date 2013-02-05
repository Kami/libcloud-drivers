from distutils.core import setup

setup(
    name='stratuslab-libcloud-drivers',
    provides=['stratuslab.libcloud'],
    version='0.2',
    author='StratusLab',
    author_email='contact@stratuslab.eu',
    url='http://stratuslab.eu/',
    license='Apache 2.0',
    description='Libcloud drivers for StratusLab clouds',
    long_description=open('README.txt').read(),

    packages=['stratuslab', 'stratuslab.libcloud'],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],

    requires=[
        "libcloud"
    ],
)
