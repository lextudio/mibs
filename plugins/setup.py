from setuptools import setup, find_packages

setup(
    name='my_plugins',  # Changed name to reflect multiple plugins
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.0',  # Add mkdocs as a dependency
    ],
    entry_points={
        'mkdocs.plugins': [
            'oid_search_plugin = plugins.oid_search_plugin:OIDSearchPlugin',
            'mib_plugin = plugins.mib_plugin:MibPlugin',
        ],
    },
    author='Your Name',
)
