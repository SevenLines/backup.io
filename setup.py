from setuptools import setup, find_packages

setup(
    name="backup.io",
    version="0.01",
    packages=find_packages(),
    long_description=open('README.rst').read(),
    entry_points={
        'console_scripts': [
            'backupio = backupio.command:main'
        ]
    },
    install_requires=[
        'terminaltables'
    ]
)