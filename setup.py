#!/usr/bin/env python3
"""Setup script for CAPTURE THE FLAG - CTF Framework."""

from setuptools import setup, find_packages
from core.constants import VERSION, APP_NAME, FULL_NAME

setup(
    name='ctf-framework',
    version=VERSION,
    description=f'{FULL_NAME} - All-in-one CLI framework for CTF challenges',
    author='CTF Team',
    python_requires='>=3.10',
    packages=find_packages(),
    install_requires=[
        'rich>=13.7.0',
        'prompt-toolkit>=3.0.43',
        'pyyaml>=6.0.1',
        'colorama>=0.4.6',
    ],
    entry_points={
        'console_scripts': [
            'ctf=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
    ],
)
