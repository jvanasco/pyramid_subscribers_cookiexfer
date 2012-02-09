"""pyramid_subscribers_cookiexfer installation script.
"""
import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.txt")).read()
README = README.split("\n\n", 1)[0] + "\n"

requires = [
    "pyramid", 
    ]

setup(name="pyramid_subscribers_cookiexfer",
      version="0.0.1",
      description="transfers cookies from request to response on exceptions",
      long_description=README,
      classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pylons",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        ],
      keywords="web pyramid",
      py_modules=['pyramid_subscribers_cookiexfer'],
      author="Jonathan Vanasco",
      author_email="jonathan@findmeon.com",
      url="https://github.com/jvanasco/pyramid_subscribers_cookiexfer",
      license="MIT",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require = requires,
      install_requires = requires,
      )

