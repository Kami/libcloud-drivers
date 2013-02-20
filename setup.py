from distutils.core import setup

setup(
    name='stratuslab-libcloud-drivers',
    version='0.8',
    author='StratusLab',
    author_email='contact@stratuslab.eu',
    url='http://stratuslab.eu/',
    license='Apache 2.0',
    description='Libcloud drivers for StratusLab clouds',
    long_description=open('README.txt').read(),

    packages=['stratuslab', 'stratuslab.libcloud'],

    install_requires=[
        "apache-libcloud ==0.11.4",
        "stratuslab-client",
        ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.6',
        'Topic :: System :: Distributed Computing',
        ],

)
