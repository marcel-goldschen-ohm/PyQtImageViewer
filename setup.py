#!/usr/bin/env python

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

setup(

    ### Metadata

    name='PyQtImageViewer',

    version='2.0.0.post1',

    description='Yet another PyQt6 or PyQt5 image viewer widget',

    long_description=(HERE / "README.md").read_text(),
    long_desc_type = "text/markdown",

    url='https://github.com/marcel-goldschen-ohm/PyQtImageViewer',

    download_url='',

    license='MIT',

    author='Marcel Goldschen-Ohm',
    author_email='goldschen-ohm@utexas.edu',

    maintainer='John Doe',
    maintainer_email='john.doe@lavabit.com',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
    ],

    ### Dependencies

    install_requires=[
        'numpy',
        'Pillow',
    ],

    ### Contents

    packages=find_packages()
    )
