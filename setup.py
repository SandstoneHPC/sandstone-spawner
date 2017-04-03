import os
import sys
from distutils.core import setup

setup_args = dict(
    name='sandstone_spawner',
    packages=['sandstone_spawner'],
    version="1.0",
    description="""Spawner class to launch Sandstone HPC user instances""",
    long_description="",
    author="Zebula Sampedro",
    author_email="sampedro@colorado.edu",
    url="https://www.rc.colorado.edu/",
    license="MIT",
    platforms="Linux, Mac OS X",
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: JavaScript',
    ],
    install_requires=[
        'jupyterhub==0.7.2',
    ]
)


def main():
    setup(**setup_args)

if __name__ == '__main__':
    main()
