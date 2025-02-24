import sys

from setuptools import setup

_ = setup(
    name="beets-importreplace",
    version="0.3",
    description="beets plugin to perform replacements on import metadata",
    long_description=open("README.md").read(),
    author="Edgars Supe",
    author_email="",
    url="https://github.com/edgars-supe/beets-importreplace",
    license="MIT",
    platforms="ALL",
    packages=["beetsplug"],
    install_requires=[
        "beets>=1.5.0",
        "typing-extensions" if sys.version_info < (3, 12) else "",
    ],
    python_requires=">=3.7",
)
