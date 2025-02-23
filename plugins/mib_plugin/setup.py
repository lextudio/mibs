from setuptools import setup, find_packages

setup(
    name='mib_plugin',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.0',  # Add mkdocs as a dependency
    ],
    entry_points={
        'mkdocs.plugins': [
            'mib_plugin = mib_plugin:MibPlugin',
        ],
    },
    author='Your Name',
)
