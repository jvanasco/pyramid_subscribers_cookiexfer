"""pyramid_subscribers_cookiexfer installation script.
"""
import os
import re

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

# store version in the init.py
with open(os.path.join(os.path.dirname(__file__),
                       'pyramid_subscribers_cookiexfer',
                       '__init__.py'
                       )
          ) as v_file:
    VERSION = re.compile(
        r".*__VERSION__ = '(.*?)'",
        re.S).match(v_file.read()).group(1)


setup(
    name="pyramid_subscribers_cookiexfer",
    version=VERSION,
    description="transfers cookies from request to response on exceptions",
    long_description=README,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
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
