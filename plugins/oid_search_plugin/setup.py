from setuptools import setup, find_packages

setup(
    name='oid_search_plugin',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.0',  # Add mkdocs as a dependency
    ],
    entry_points={
        'mkdocs.plugins': [
            'oid_search_plugin = oid_search_plugin:OIDSearchPlugin',
        ],
    },
    author='Your Name',
)
