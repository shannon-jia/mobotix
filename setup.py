#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0',
                'aiohttp>=3.1.2',
                'asynqp>=0.5.1']

setup_requirements = []

test_requirements = []

setup(
    author="Shannon-Li",
    author_email='lishengchen@mingvale.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Mobotix for SAM V1 with RabbitMQ",
    entry_points={
        'console_scripts': [
            'sam-mobotix=mobotix.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='mobotix',
    name='mobotix',
    packages=find_packages(include=['mobotix']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/shannon-jia/mobotix',
    version='0.1.0',
    zip_safe=False,
)
