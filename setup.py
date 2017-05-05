# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='sandstone-spawner',
    version='0.1.0',
    author=u'Zebula Sampedro',
    author_email='sampedro@colorado.edu',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/SandstoneHPC/sandstone-spawner',
    license='MIT, see LICENSE',
    description=open('DESCRIPTION.rst').read(),
    long_description='',
    zip_safe=False,
    install_requires=[
        'jupyterhub==0.7.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: Unix',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)',
        'License :: OSI Approved :: MIT License',
    ]
)
