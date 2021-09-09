from setuptools import setup

setup(
    name='beets-importreplace',
    version='0.1.1',
    description='beets plugin to perform replacements on import metadata',
    long_description=open('README.md').read(),
    author='Edgars Supe',
    author_email='',
    url='https://github.com/edgars-supe/beets-importreplace',
    license='MIT',
    platforms='ALL',
    packages=['beetsplug'],
    install_requires=['beets>=1.4.7'],
)
