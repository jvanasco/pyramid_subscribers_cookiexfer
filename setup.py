"""pyramid_subscribers_cookiexfer installation script.
"""
import os

from setuptools import setup
from setuptools import find_packages

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, "README.md")).read()
    README = README.split("\n\n", 1)[0] + "\n"
except:
    README = ''

requires = [
    "pyramid",
]

setup(
    name="pyramid_subscribers_cookiexfer",
    version="0.0.7",
    description="transfers cookies from request to response on exceptions",
    long_description=README,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="web pyramid",
    packages=['pyramid_subscribers_cookiexfer'],
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    url="https://github.com/jvanasco/pyramid_subscribers_cookiexfer",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    tests_require = requires,
    install_requires = requires,
    test_suite='tests',
)
