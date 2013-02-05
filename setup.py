from distutils.core import setup

setup(
    name='stratuslab-libcloud-drivers',
    version='0.4',
    author='StratusLab',
    author_email='contact@stratuslab.eu',
    url='http://stratuslab.eu/',
    license='Apache 2.0',
    description='Libcloud drivers for StratusLab clouds',
    long_description=open('README.txt').read(),

    packages=['stratuslab', 'stratuslab.libcloud'],

    install_requires=[
        "apache-libcloud >= 0.11.4",
        "stratuslab-client == 13.02.dev",
    ],
)
