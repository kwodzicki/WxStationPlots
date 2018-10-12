#!/usr/bin/env python
from setuptools import setup
import setuptools


setuptools.setup(
  name             = "WxStationPlots",
  description      = "For generating meteorological station plots on maps",
  url              = "https://github.com/kwodzicki/WxStationPlots",
  author           = "Kyle R. Wodzicki",
  author_email     = "krwodzicki@gmail.com",
  version          = "0.0.2",
  packages         = setuptools.find_packages(),
  install_requires = [ "python-awips", "cartopy", "matplotlib", "numpy", "scipy", "metpy", "psutil" ],
  scripts          = None,
  zip_safe = False
);
