from setuptools import setup, find_packages

setup(
    name='pipeline_cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'pipeline=pipeline_cli.main:main',
        ],
    },
)