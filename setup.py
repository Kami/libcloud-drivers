from distutils.core import setup

setup(
    name='stratuslab-libcloud-drivers',
    version='0.1',
    author='StratusLab',
    author_email='contact@stratuslab.eu',
    packages=['lcsl.compute.drivers'],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/stratuslab-libcloud-drivers/',
    license='LICENSE',
    description='Libcloud drivers for StratusLab clouds',
    long_description=open('README.txt').read(),
    install_requires=[
        "apache-libcloud >= 0.11.4"
    ],
)
