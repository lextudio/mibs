from setuptools import setup, find_packages

setup(
    name='mib_plugin',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'mib_plugin = mib_plugin.mib_plugin:MibPlugin',
        ]
    }
)
